// OAuth2 PKCE flow for Microsoft identity — no external packages required.
// Authenticates against the Pyrovio production tenant so the app can read
// SharePoint lists even when running under a Sandbox Power Apps account.

const CLIENT_ID   = '4b0d466f-5e26-49a7-b3e9-345a79268090';
const TENANT_ID   = 'add0151d-6436-4f59-a424-e401b0363d09';
const REDIRECT_URI = 'https://apps.powerapps.com/play/e/default-1b4e0c69-9f47-4349-b384-3445e56fa363/app/f5c17ed7-2e10-475c-9234-e4910d6af4be';
const SCOPES      = 'openid profile User.Read Sites.ReadWrite.All';
const TOKEN_KEY   = 'pto_graph_token';
const EXPIRY_KEY  = 'pto_graph_token_expiry';

// ---------- PKCE helpers ----------

function base64url(buf: ArrayBuffer): string {
  return btoa(String.fromCharCode(...new Uint8Array(buf)))
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

async function generatePkce(): Promise<{ verifier: string; challenge: string }> {
  const verifierBytes = crypto.getRandomValues(new Uint8Array(32));
  const verifier = base64url(verifierBytes.buffer);
  const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
  return { verifier, challenge: base64url(hash) };
}

function randomState(): string {
  return base64url(crypto.getRandomValues(new Uint8Array(16)).buffer);
}

// ---------- Token cache ----------

function getCachedToken(): string | null {
  const token  = localStorage.getItem(TOKEN_KEY);
  const expiry = Number(localStorage.getItem(EXPIRY_KEY) ?? 0);
  if (!token || Date.now() >= expiry - 60_000) return null;
  return token;
}

function cacheToken(token: string, expiresInSeconds: number): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(EXPIRY_KEY, String(Date.now() + expiresInSeconds * 1000));
}

// ---------- Auth code exchange ----------

async function exchangeCode(code: string, verifier: string): Promise<string | null> {
  const body = new URLSearchParams({
    client_id:     CLIENT_ID,
    grant_type:    'authorization_code',
    code,
    redirect_uri:  REDIRECT_URI,
    code_verifier: verifier,
    scope:         SCOPES,
  });

  try {
    const res = await fetch(
      `https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token`,
      { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body },
    );
    if (!res.ok) return null;
    const json = await res.json();
    if (json.access_token) cacheToken(json.access_token, json.expires_in ?? 3600);
    return json.access_token ?? null;
  } catch {
    return null;
  }
}

// ---------- Popup login ----------

let loginPromise: Promise<string | null> | null = null;

async function loginWithPopup(): Promise<string | null> {
  const { verifier, challenge } = await generatePkce();
  const state = randomState();

  const authUrl = new URL(`https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize`);
  authUrl.searchParams.set('client_id',              CLIENT_ID);
  authUrl.searchParams.set('response_type',          'code');
  authUrl.searchParams.set('redirect_uri',           REDIRECT_URI);
  authUrl.searchParams.set('scope',                  SCOPES);
  authUrl.searchParams.set('state',                  state);
  authUrl.searchParams.set('code_challenge',         challenge);
  authUrl.searchParams.set('code_challenge_method',  'S256');
  authUrl.searchParams.set('prompt',                 'select_account');

  const popup = window.open(authUrl.toString(), 'mslogin', 'width=480,height=640,left=200,top=100');
  if (!popup) return null;

  return new Promise((resolve) => {
    const timer = setInterval(async () => {
      try {
        const url = new URL(popup.location.href);
        if (url.origin !== window.location.origin && !url.href.startsWith(REDIRECT_URI)) return;

        clearInterval(timer);
        popup.close();

        const code = url.searchParams.get('code');
        const returnedState = url.searchParams.get('state');
        if (!code || returnedState !== state) { resolve(null); return; }

        resolve(await exchangeCode(code, verifier));
      } catch {
        // popup not yet at redirect URI — still on login.microsoftonline.com
        if (popup.closed) { clearInterval(timer); resolve(null); }
      }
    }, 500);
  });
}

// ---------- Public API ----------

export async function getGraphToken(): Promise<string | null> {
  const cached = getCachedToken();
  if (cached) return cached;

  if (!loginPromise) {
    loginPromise = loginWithPopup().finally(() => { loginPromise = null; });
  }
  return loginPromise;
}
