// بازی پیشرفته کهکشانی - سیستم جاوااسکریپت

class GalaxyGameEngine {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.isInitialized = false;
        this.audioContext = null;
        this.touchController = null;
    }

    // راه‌اندازی موتور بازی
    async initialize() {
        try {
            this.canvas = document.getElementById('mainCanvas');
            this.ctx = this.canvas.getContext('2d');
            
            // راه‌اندازی سیستم صدا
            await this.initializeAudio();
            
            // راه‌اندازی کنترل لمسی
            this.initializeTouchControls();
            
            // راه‌اندازی WebGL برای گرافیک پیشرفته
            await this.initializeWebGL();
            
            this.isInitialized = true;
            console.log('🚀 Galaxy Game Engine Initialized Successfully');
        } catch (error) {
            console.error('Error initializing game engine:', error);
        }
    }

    // راه‌اندازی سیستم صدا
    async initializeAudio() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // بارگذاری صداها
        this.sounds = {
            explosion: await this.loadSound('sounds/explosion.mp3'),
            coin: await this.loadSound('sounds/coin.mp3'),
            engine: await this.loadSound('sounds/engine.mp3'),
            background: await this.loadSound('sounds/background.mp3')
        };
    }

    // بارگذاری فایل صوتی
    async loadSound(url) {
        try {
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            return audioBuffer;
        } catch (error) {
            console.warn('Could not load sound:', url);
            return null;
        }
    }

    // پخش صدا
    playSound(soundBuffer, volume = 1.0, playbackRate = 1.0) {
        if (!soundBuffer || this.audioContext.state === 'suspended') return;
        
        const source = this.audioContext.createBufferSource();
        const gainNode = this.audioContext.createGain();
        
        source.buffer = soundBuffer;
        source.playbackRate.value = playbackRate;
        gainNode.gain.value = volume;
        
        source.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        source.start();
    }

    // راه‌اندازی کنترل‌های لمسی
    initializeTouchControls() {
        this.touchController = {
            isTouching: false,
            startX: 0,
            startY: 0,
            currentX: 0,
            currentY: 0,
            sensitivity: 0.02
        };

        const joystickArea = document.querySelector('.joystick-area');
        
        joystickArea.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = joystickArea.getBoundingClientRect();
            
            this.touchController.isTouching = true;
            this.touchController.startX = touch.clientX - rect.left;
            this.touchController.startY = touch.clientY - rect.top;
        });

        joystickArea.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!this.touchController.isTouching) return;
            
            const touch = e.touches[0];
            const rect = joystickArea.getBoundingClientRect();
            
            this.touchController.currentX = touch.clientX - rect.left;
            this.touchController.currentY = touch.clientY - rect.top;
            
            this.updateJoystickPosition();
        });

        joystickArea.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.touchController.isTouching = false;
            this.touchController.currentX = this.touchController.startX;
            this.touchController.currentY = this.touchController.startY;
            this.updateJoystickPosition();
        });
    }

    // به‌روزرسانی موقعیت جویستیک
    updateJoystickPosition() {
        const deltaX = this.touchController.currentX - this.touchController.startX;
        const deltaY = this.touchController.currentY - this.touchController.startY;
        
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const maxDistance = 50; // شعاع جویستیک
        
        if (distance > maxDistance) {
            const angle = Math.atan2(deltaY, deltaX);
            this.touchController.currentX = this.touchController.startX + Math.cos(angle) * maxDistance;
            this.touchController.currentY = this.touchController.startY + Math.sin(angle) * maxDistance;
        }
        
        // ارسال موقعیت به Blazor
        const normalizedX = (this.touchController.currentX - this.touchController.startX) * this.touchController.sensitivity;
        const normalizedY = (this.touchController.currentY - this.touchController.startY) * this.touchController.sensitivity;
        
        DotNet.invokeMethodAsync('GalaxyAdvancedGame', 'UpdateJoystick', normalizedX, normalizedY);
    }

    // راه‌اندازی WebGL برای گرافیک سه‌بعدی
    async initializeWebGL() {
        try {
            this.gl = this.canvas.getContext('webgl2') || this.canvas.getContext('webgl');
            
            if (!this.gl) {
                console.warn('WebGL not supported, falling back to 2D');
                return;
            }

            // کامپایل شیدرها
            this.program = this.createShaderProgram(vertexShaderSource, fragmentShaderSource);
            
            // ایجاد بافرها
            this.setupBuffers();
            
            // بارگذاری بافت‌ها
            await this.loadTextures();
            
            console.log('🎮 WebGL Initialized Successfully');
        } catch (error) {
            console.warn('WebGL initialization failed:', error);
        }
    }

    // شیدرهای GLSL برای گرافیک پیشرفته
    createShaderProgram(vertexSource, fragmentSource) {
        const vertexShader = this.compileShader(this.gl.VERTEX_SHADER, vertexSource);
        const fragmentShader = this.compileShader(this.gl.FRAGMENT_SHADER, fragmentSource);
        
        const program = this.gl.createProgram();
        this.gl.attachShader(program, vertexShader);
        this.gl.attachShader(program, fragmentShader);
        this.gl.linkProgram(program);
        
        if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
            console.error('Shader program error:', this.gl.getProgramInfoLog(program));
        }
        
        return program;
    }

    // کامپایل شیدر
    compileShader(type, source) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);
        
        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error('Shader compile error:', this.gl.getShaderInfoLog(shader));
            this.gl.deleteShader(shader);
            return null;
        }
        
        return shader;
    }

    // تابع‌های کمکی
    getWindowWidth() {
        return window.innerWidth;
    }

    getWindowHeight() {
        return window.innerHeight;
    }

    playExplosionSound() {
        this.playSound(this.sounds.explosion, 0.7);
    }

    playCoinSound() {
        this.playSound(this.sounds.coin, 0.5);
    }

    startBackgroundMusic() {
        if (this.sounds.background) {
            this.playSound(this.sounds.background, 0.3);
        }
    }
}

// شیدرهای GLSL
const vertexShaderSource = `
    attribute vec2 aPosition;
    attribute vec2 aTexCoord;
    varying vec2 vTexCoord;
    
    void main() {
        gl_Position = vec4(aPosition, 0.0, 1.0);
        vTexCoord = aTexCoord;
    }
`;

const fragmentShaderSource = `
    precision mediump float;
    varying vec2 vTexCoord;
    uniform sampler2D uTexture;
    uniform float uTime;
    
    void main() {
        vec2 uv = vTexCoord;
        
        // افکت کهکشان پویا
        uv.x += sin(uv.y * 10.0 + uTime) * 0.01;
        uv.y += cos(uv.x * 8.0 + uTime) * 0.008;
        
        vec4 color = texture2D(uTexture, uv);
        
        // افزودن درخشش
        color.rgb += sin(uTime * 2.0) * 0.1;
        
        gl_FragColor = color;
    }
`;

// راه‌اندازی موتور بازی
let gameEngine;

window.initializeGameEngine = async function() {
    gameEngine = new GalaxyGameEngine();
    await gameEngine.initialize();
    return true;
};

window.getWindowWidth = () => gameEngine ? gameEngine.getWindowWidth() : window.innerWidth;
window.getWindowHeight = () => gameEngine ? gameEngine.getWindowHeight() : window.innerHeight;
window.playExplosionSound = () => gameEngine ? gameEngine.playExplosionSound() : null;
window.playCoinSound = () => gameEngine ? gameEngine.playCoinSound() : null;
