const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 3000;
const JWT_SECRET = 'your-secret-key';

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Mock user database
const users = [
    {
        id: 1,
        username: 'admin',
        password: 'password123', // In production, this should be hashed
        role: 'admin'
    }
];

// Authentication middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Access denied' });
    }

    try {
        const verified = jwt.verify(token, JWT_SECRET);
        req.user = verified;
        next();
    } catch (err) {
        res.status(400).json({ error: 'Invalid token' });
    }
};

// Login route
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;

    // Find user
    const user = users.find(u => u.username === username);
    if (!user) {
        return res.status(401).json({
            error: 'ACCESS DENIED: User not found'
        });
    }

    // Verify password (in production, use proper password hashing)
    if (password !== user.password) {
        return res.status(401).json({
            error: 'ACCESS DENIED: Invalid password'
        });
    }

    // Create token
    const token = jwt.sign(
        { id: user.id, username: user.username, role: user.role },
        JWT_SECRET,
        { expiresIn: '1h' }
    );

    res.json({
        message: 'ACCESS GRANTED',
        token,
        user: {
            id: user.id,
            username: user.username,
            role: user.role
        }
    });
});

// Protected route example
app.get('/api/protected', authenticateToken, (req, res) => {
    res.json({
        message: 'This is a protected route',
        user: req.user
    });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
