const { app, BrowserWindow, globalShortcut, ipcMain, Tray, Menu, screen, nativeImage, systemPreferences } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const http = require('http');

const PROJECT = path.join(__dirname, '..');
// Find the project's Python: Windows .venv, or macOS/Linux venv / .venv.
function findPython() {
  const candidates = [
    path.join(PROJECT, '.venv', 'Scripts', 'python.exe'),
    path.join(PROJECT, '.venv', 'bin', 'python'),
    path.join(PROJECT, 'venv', 'bin', 'python'),
    path.join(PROJECT, 'venv', 'Scripts', 'python.exe'),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}
const PY = findPython();
const SERVER_URL = 'http://localhost:8340';

// Optional cache redirects (off the system drive). Read from config.json so this
// isn't hardcoded to one machine's A: drive — omit the keys and the defaults win.
function loadConfig() {
  try {
    return JSON.parse(fs.readFileSync(path.join(PROJECT, 'config.json'), 'utf8'));
  } catch {
    return {};
  }
}
const CONFIG = loadConfig();

let win = null;
let tray = null;
let serverProc = null;

function ping(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => { res.resume(); resolve(true); });
    req.on('error', () => resolve(false));
    req.setTimeout(1500, () => { req.destroy(); resolve(false); });
  });
}

async function ensureServer() {
  if (await ping(SERVER_URL)) return; // already running
  const cacheEnv = {};
  if (CONFIG.ollama_models_path) cacheEnv.OLLAMA_MODELS = CONFIG.ollama_models_path;
  if (CONFIG.playwright_browsers_path) cacheEnv.PLAYWRIGHT_BROWSERS_PATH = CONFIG.playwright_browsers_path;
  serverProc = spawn(PY, ['server.py'], {
    cwd: PROJECT,
    env: Object.assign({}, process.env, cacheEnv),
    windowsHide: true,
  });
  serverProc.stdout.on('data', (d) => process.stdout.write('[server] ' + d));
  serverProc.stderr.on('data', (d) => process.stdout.write('[server] ' + d));
  for (let i = 0; i < 90; i++) {
    if (await ping(SERVER_URL)) return;
    await new Promise((r) => setTimeout(r, 1000));
  }
}

function createWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  const W = 380, H = 560;
  win = new BrowserWindow({
    width: W,
    height: H,
    x: width - W - 24,
    y: height - H - 24,
    icon: path.join(__dirname, 'icon.ico'),
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    skipTaskbar: false,
    hasShadow: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      autoplayPolicy: 'no-user-gesture-required',
    },
  });
  // Allow only what the HUD needs (microphone) — deny camera, geolocation, etc.
  win.webContents.session.setPermissionRequestHandler((wc, permission, callback) => {
    callback(permission === 'media');
  });
  win.setAlwaysOnTop(true, 'screen-saver');
  win.loadURL(SERVER_URL + '/?hud=1');
}

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) app.quit();
app.on('second-instance', () => {
  if (win) { if (win.isMinimized()) win.restore(); win.show(); win.focus(); }
});

app.whenReady().then(async () => {
  if (!gotTheLock) return;
  if (process.platform === 'darwin') {
    try { await systemPreferences.askForMediaAccess('microphone'); } catch (e) {}
  }
  await ensureServer();
  createWindow();

  globalShortcut.register('Alt+Z', () => {
    if (win) win.webContents.send('toggle-listen');
  });

  try {
    let trayIcon = nativeImage.createFromPath(path.join(__dirname, 'icon.png'));
    if (process.platform === 'darwin') trayIcon = trayIcon.resize({ width: 18, height: 18 });
    tray = new Tray(trayIcon);
    const menu = Menu.buildFromTemplate([
      { label: 'Toggle listening (Option+Z)', click: () => win && win.webContents.send('toggle-listen') },
      { label: 'Show / Hide', click: () => { if (!win) return; win.isVisible() ? win.hide() : win.show(); } },
      { type: 'separator' },
      { label: 'Quit', click: () => app.quit() },
    ]);
    tray.setToolTip('E.V.');
    tray.setContextMenu(menu);
    tray.on('click', () => { if (win) { win.isVisible() ? win.hide() : win.show(); } });
  } catch (e) {
    console.log('Tray setup failed:', e.message);
  }
});

const COMPACT = { w: 380, h: 560 };
ipcMain.on('set-mode', (e, mode) => {
  if (!win) return;
  if (mode === 'dashboard') {
    win.setAlwaysOnTop(false);
    win.setResizable(true);
    win.maximize();
  } else {
    win.unmaximize();
    win.setResizable(false);
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    win.setBounds({ x: width - COMPACT.w - 24, y: height - COMPACT.h - 24, width: COMPACT.w, height: COMPACT.h });
    win.setAlwaysOnTop(true, 'screen-saver');
  }
});

ipcMain.on('quit', () => app.quit());
ipcMain.on('hide', () => { if (win) win.hide(); });
// Show without stealing focus from the app the user is in.
ipcMain.on('show', () => { if (win) win.showInactive(); });

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  if (serverProc && !serverProc.killed) {
    try { serverProc.kill(); } catch (e) {}
  }
});

app.on('window-all-closed', () => app.quit());
