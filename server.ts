import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';
import { randomUUID } from 'node:crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  console.log('Starting server...');
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: '50mb' }));

  // In-memory Global Store for materials
  let GLOBAL_STORE: any[] = [];
  let USERS: any[] = [
    { id: '1', username: 'admin', password: 'admin', email: 'admin@e-listen.com', role: 'admin' }
  ];

  // API Routes
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  app.post('/api/auth/login', (req, res) => {
    console.log(`Login attempt for: ${req.body.username}`);
    const { username, password } = req.body;
    const user = USERS.find(u => u.username === username && u.password === password);
    if (user) {
      const { password, ...userWithoutPassword } = user;
      res.json({ success: true, user: userWithoutPassword });
    } else {
      res.status(401).json({ error: '用户名或密码错误' });
    }
  });

  app.post('/api/auth/register', (req, res) => {
    console.log(`Register attempt for: ${req.body.username}`);
    const { username, password } = req.body;
    if (USERS.find(u => u.username === username)) {
      return res.status(400).json({ error: '用户名已存在' });
    }
    const newUser = { id: randomUUID(), username, password, email: '', role: 'user' };
    USERS.push(newUser);
    const { password: _, ...userWithoutPassword } = newUser;
    res.json({ success: true, user: userWithoutPassword });
  });

  app.get('/api/materials', (req, res) => {
    res.json(GLOBAL_STORE);
  });

  app.post('/api/materials/sync', (req, res) => {
    const { materials } = req.body;
    if (Array.isArray(materials)) {
      // Basic merge logic: replace or merge based on ID
      // For this demo, we'll just replace the global store with the latest sync if it's more comprehensive
      // or simply maintain a master list by ID.
      materials.forEach(newM => {
        const index = GLOBAL_STORE.findIndex(m => m.id === newM.id);
        if (index !== -1) {
          // Only update if the incoming one is newer
          if (newM.lastModified > GLOBAL_STORE[index].lastModified) {
            GLOBAL_STORE[index] = newM;
          }
        } else {
          GLOBAL_STORE.push(newM);
        }
      });
      
      // Sort by lastModified
      GLOBAL_STORE.sort((a, b) => b.lastModified - a.lastModified);
      
      res.json({ success: true, count: GLOBAL_STORE.length });
    } else {
      res.status(400).json({ error: 'Invalid materials data' });
    }
  });

  app.delete('/api/materials/:id', (req, res) => {
    const { id } = req.params;
    GLOBAL_STORE = GLOBAL_STORE.filter(m => m.id !== id);
    res.json({ success: true });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
