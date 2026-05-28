/**
 * intakeAutoConvert — shared helper that takes an approved (or auto-approved)
 * project request and:
 *
 *   1. Appends an "approved" entry to the approval chain.
 *   2. Audits the intake approval (so /admin/change-history shows it even if
 *      the project is later deleted).
 *   3. Creates the project (or program) via the appropriate mutation.
 *   4. For project conversions: creates the primary-team membership row,
 *      applies the resolved template, and carries over stage artifacts.
 *      All three are best-effort and log a warning rather than aborting.
 *   5. PATCHes the request to bind ConvertedProject/Program, flips status
 *      to Converted, writes the converted-date, and persists the chain.
 *      Throws a HALF_CONVERTED error if this final step fails so the caller
 *      can surface a loud "created (id) but request not updated" toast.
 *
 * Extracted from StageApprovalPanel.handleApprove so the GovernedIntakeWizard
 * can reuse the same sequence when the intake.bypassApproval admin toggle is
 * on. Keep this function pure of UI concerns — callers own toasts, dialogs,
 * and navigation.
 */

import { updateProjectRequest } from '../api/projectRequests.api';
import { createProjectTeam } from '../api/projectTeams.api';
import { applyProjectTemplate } from './schedulingClient';
import { resolveTemplate } from './templateResolution';
import { readExtras } from './intakeExtras';
import {
  buildProjectPayload, buildProgramPayload, carryOverArtifacts,
} from './intakeConversion';
import {
  REQUEST_STATUS, CONVERSION_TARGET, TEAM_ROLE,
} from './constants';
import type { ProjectRequest } from '../models/projectRequest.model';
import type { ApprovalAction } from './intakeValidation';
import type { AppSetting } from '../api/appSettings.api';
import type { ProjectTemplate } from '../models/projectTemplate.model';
import type { useCreateProject } from '../hooks/useProjects';
import type { useCreateProgram } from '../hooks/usePrograms';
import type { useChangeAudit } from '../hooks/useChangeAudit';

export class HalfConvertedError extends Error {
  createdId: string;
  kind: 'project' | 'program';
  constructor(createdId: string, kind: 'project' | 'program', cause?: unknown) {
    super(
      `${kind === 'program' ? 'Program' : 'Project'} created (${createdId}) but request not updated. ` +
      `Refresh and re-run conversion or contact admin.`,
    );
    this.name = 'HalfConvertedError';
    this.createdId = createdId;
    this.kind = kind;
    if (cause !== undefined) (this as { cause?: unknown }).cause = cause;
  }
}

export interface AutoApproveAndConvertArgs {
  request: ProjectRequest;
  /** Persisted approval chain to append the new "approved" entry to. */
  approvalChain: ApprovalAction[];
  /** Stage order to record on the new chain entry (use current stage index). */
  stageOrder: number;
  /** Current systemuserid. Falls back to empty string if unresolved. */
  currentUserId: string;
  /** Rationale text persisted on the chain entry. Distinguishes manual
   *  approval from the auto-bypass path in change history. */
  approvalRationale: string;
  /** App settings array (for template resolution). */
  settings: AppSetting[] | undefined;
  /** Project templates (for template resolution). */
  templates: ProjectTemplate[] | undefined;
  /** Mutation hook returned from useCreateProject(). */
  createProject: ReturnType<typeof useCreateProject>;
  /** Mutation hook returned from useCreateProgram(). */
  createProgram: ReturnType<typeof useCreateProgram>;
  /** Audit hook returned from useChangeAudit(). */
  auditChange: ReturnType<typeof useChangeAudit>;
}

export interface AutoApproveAndConvertResult {
  createdId: string;
  kind: 'project' | 'program';
}

export async function autoApproveAndConvert(
  args: AutoApproveAndConvertArgs,
): Promise<AutoApproveAndConvertResult> {
  const {
    request, approvalChain, stageOrder, currentUserId, approvalRationale,
    settings, templates, createProject, createProgram, auditChange,
  } = args;

  const isProgram = request.pmo_conversiontarget === CONVERSION_TARGET.Program;
  const entityName = request.pmo_name ?? 'Untitled Request';

  // 1) Build and append the approval-chain entry.
  const newEntry: ApprovalAction = {
    stageOrder,
    action: 'approved',
    actorId: currentUserId,
    actorName: 'Current User',
    timestamp: new Date().toISOString(),
    rationale: approvalRationale,
  };
  const chain = [...approvalChain, newEntry];

  // 2) Audit the intake approval itself.
  auditChange({
    entityType: 'intake',
    entityId: request.pmo_projectrequestid,
    entityName,
    action: 'approve',
    changes: [
      { kind: 'field', field: 'pmo_status', label: 'Status',    old: 'Submitted', new: 'Approved' },
      { kind: 'field', field: 'rationale',  label: 'Rationale', old: null,        new: approvalRationale },
    ],
  });

  // 3) Create the project or program.
  let createdId: string;
  const kind: 'project' | 'program' = isProgram ? 'program' : 'project';

  if (isProgram) {
    const program = await createProgram.mutateAsync(buildProgramPayload(request));
    createdId = program.msdyn_projectprogramid;
    auditChange({
      entityType: 'program',
      entityId: createdId,
      entityName,
      action: 'create',
    });
  } else {
    const project = await createProject.mutateAsync(buildProjectPayload(request));
    createdId = project.msdyn_projectid;
    auditChange({
      entityType: 'project',
      entityId: createdId,
      entityName,
      action: 'create',
      parentProjectId: createdId,
      parentProjectName: entityName,
    });

    // 4a) Primary-team membership row (best effort).
    const teamId = request['_pmo_targetteam_value'];
    if (teamId) {
      try {
        await createProjectTeam({
          'pmo_Project@odata.bind': `/msdyn_projects(${createdId})`,
          'pmo_Team@odata.bind': `/teams(${teamId})`,
          pmo_role: TEAM_ROLE.Primary,
          pmo_joineddate: new Date().toISOString().split('T')[0],
        });
      } catch (err) {
        console.warn('Primary-team row creation failed (non-fatal):', err);
      }
    }

    // 4b) Template application (best effort).
    try {
      const settingMap = Object.fromEntries((settings ?? []).map((s) => [s.pmo_key, s]));
      const { tasks } = resolveTemplate({
        settingMap,
        templates: templates ?? [],
        primaryTeamId: teamId ?? undefined,
        cfrCategory: readExtras(request).cfrCategory,
      });
      if (tasks.length > 0) await applyProjectTemplate(createdId, tasks);
    } catch (err) {
      console.warn('Template application failed (non-fatal):', err);
    }

    // 4c) Artifact carry-over (best effort).
    if (request.pmo_stageartifactsjson) {
      try {
        await carryOverArtifacts(
          request.pmo_stageartifactsjson,
          createdId,
          readExtras(request).cfrCategory,
        );
      } catch (err) {
        console.warn('Artifact carry-over failed (non-fatal):', err);
      }
    }
  }

  // 5) PATCH the request — bind converted project/program, status=Converted.
  try {
    const bindKey = isProgram
      ? 'pmo_ConvertedProgram@odata.bind' : 'pmo_ConvertedProject@odata.bind';
    const bindEntity = isProgram ? 'msdyn_projectprograms' : 'msdyn_projects';
    const patchPayload: Record<string, unknown> = {
      pmo_approvalchain: JSON.stringify(chain),
      pmo_currentstagenumber: stageOrder,
      pmo_status: REQUEST_STATUS.Converted,
      pmo_converteddate: new Date().toISOString().split('T')[0],
      [bindKey]: `/${bindEntity}(${createdId})`,
    };
    await updateProjectRequest(request.pmo_projectrequestid, patchPayload);
  } catch (patchErr) {
    console.error('Half-converted request:', request.pmo_projectrequestid, patchErr);
    throw new HalfConvertedError(createdId, kind, patchErr);
  }

  return { createdId, kind };
}
