const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  // Create menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'View',
      submenu: [
        { label: 'Home', click: () => mainWindow.loadFile('landing.html') },
        { label: 'Detection', click: () => mainWindow.loadFile('detection.html') },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'toggleDevTools' }
      ]
    },
    {
      label: 'Server',
      submenu: [
        { 
          label: 'Start Python Server', 
          click: () => startPythonServer() 
        },
        { 
          label: 'Stop Python Server', 
          click: () => stopPythonServer() 
        }
      ]
    }
  ]);
  Menu.setApplicationMenu(menu);

  mainWindow.loadFile('landing.html');

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startPythonServer() {
  if (pythonProcess) {
    console.log('Python server is already running');
    return;
  }

  console.log('Starting Python server...');
  
  const serverPath = path.join(__dirname, 'backend', 'server.py');
  pythonProcess = spawn('python', [serverPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python server exited with code ${code}`);
    pythonProcess = null;
  });
}

function stopPythonServer() {
  if (pythonProcess) {
    console.log('Stopping Python server...');
    pythonProcess.kill();
    pythonProcess = null;
  }
}

app.on('ready', () => {
  createWindow();
  // Auto-start Python server (optional)
  // startPythonServer();
});

app.on('window-all-closed', () => {
  stopPythonServer();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', () => {
  stopPythonServer();
});
