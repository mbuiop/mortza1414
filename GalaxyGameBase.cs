using Microsoft.AspNetCore.Components;
using Blazor.Extensions;
using Blazor.Extensions.Canvas;
using Blazor.Extensions.Canvas.Model;
using System.Timers;
using Microsoft.JSInterop;

namespace GalaxyAdvancedGame.Components
{
    public class GalaxyGameBase : ComponentBase
    {
        [Inject] protected IJSRuntime JSRuntime { get; set; }
        
        // بازی وضعیت
        protected bool gameRunning = false;
        protected bool showMainMenu = true;
        protected bool showLevelComplete = false;
        
        // اطلاعات بازیکن
        protected double playerX = 400;
        protected double playerY = 300;
        protected double playerRotation = 0;
        protected double playerSpeed = 5;
        protected double playerFuel = 100;
        protected int currentScore = 0;
        protected int currentLevel = 1;
        protected int coinsCollected = 0;
        
        // سیستم بمب
        protected bool bombAvailable = true;
        protected double bombCooldown = 0;
        protected bool isSafeTime = false;
        protected double safeTimeRemaining = 0;
        
        // کنترل لمسی
        protected double joystickX = 0;
        protected double joystickY = 0;
        protected bool isTouching = false;
        protected double touchStartX = 0;
        protected double touchStartY = 0;
        
        // اشیاء بازی
        protected List<GameCoin> coins = new();
        protected List<GameEnemy> enemies = new();
        protected List<GameEffect> effects = new();
        
        // آمار
        protected int highScore = 0;
        protected int maxLevel = 1;
        protected int totalCoins = 0;
        
        // گرافیک و صدا
        protected Canvas2DContext canvasContext;
        protected System.Timers.Timer gameTimer;
        protected DotNetObjectReference<GalaxyGameBase> dotNetRef;
        
        protected override void OnInitialized()
        {
            dotNetRef = DotNetObjectReference.Create(this);
            InitializeGameTimer();
        }
        
        private void InitializeGameTimer()
        {
            gameTimer = new System.Timers.Timer(16); // 60 FPS
            gameTimer.Elapsed += async (s, e) => await GameUpdate();
            gameTimer.AutoReset = true;
        }
        
        protected async Task GameUpdate()
        {
            if (!gameRunning) return;
            
            await InvokeAsync(async () =>
            {
                UpdatePlayer();
                UpdateEnemies();
                UpdateCoins();
                UpdateEffects();
                UpdateGameSystems();
                CheckCollisions();
                StateHasChanged();
            });
        }
        
        protected void UpdatePlayer()
        {
            // حرکت بازیکن بر اساس جویستیک
            if (isTouching)
            {
                playerX += joystickX * playerSpeed;
                playerY += joystickY * playerSpeed;
                
                // محدود کردن به مرزهای صفحه
                playerX = Math.Max(30, Math.Min(windowWidth - 30, playerX));
                playerY = Math.Max(30, Math.Min(windowHeight - 30, playerY));
                
                // به‌روزرسانی چرخش
                if (joystickX != 0 || joystickY != 0)
                {
                    playerRotation = Math.Atan2(joystickY, joystickX);
                }
            }
        }
        
        protected void UpdateGameSystems()
        {
            // سیستم سوخت
            playerFuel = Math.Max(0, playerFuel - 0.05);
            if (playerFuel <= 0)
            {
                GameOver();
            }
            
            // سیستم بمب
            if (bombCooldown > 0)
            {
                bombCooldown = Math.Max(0, bombCooldown - 0.016);
                bombAvailable = bombCooldown <= 0;
            }
            
            // زمان امن
            if (isSafeTime)
            {
                safeTimeRemaining = Math.Max(0, safeTimeRemaining - 0.016);
                if (safeTimeRemaining <= 0)
                {
                    isSafeTime = false;
                }
            }
        }
        
        protected async void ActivateBomb()
        {
            if (!bombAvailable || !gameRunning) return;
            
            bombAvailable = false;
            bombCooldown = 10; // 10 ثانیه
            isSafeTime = true;
            safeTimeRemaining = 5; // 5 ثانیه زمان امن
            
            // نابودی تمام دشمنان
            foreach (var enemy in enemies)
            {
                effects.Add(new GameEffect
                {
                    X = enemy.X,
                    Y = enemy.Y,
                    Type = EffectType.Explosion,
                    LifeTime = 1.0
                });
            }
            enemies.Clear();
            
            // پخش صدا
            await JSRuntime.InvokeVoidAsync("playExplosionSound");
        }
        
        protected void CheckCollisions()
        {
            // برخورد با سکه‌ها
            for (int i = coins.Count - 1; i >= 0; i--)
            {
                var coin = coins[i];
                var distance = Math.Sqrt(Math.Pow(playerX - coin.X, 2) + Math.Pow(playerY - coin.Y, 2));
                
                if (distance < 40) // شعاع برخورد
                {
                    CollectCoin(coin);
                    coins.RemoveAt(i);
                }
            }
            
            // برخورد با دشمنان (فقط در زمان غیرامن)
            if (!isSafeTime)
            {
                foreach (var enemy in enemies)
                {
                    var distance = Math.Sqrt(Math.Pow(playerX - enemy.X, 2) + Math.Pow(playerY - enemy.Y, 2));
                    
                    if (distance < 35)
                    {
                        HandleEnemyCollision(enemy);
                        break;
                    }
                }
            }
        }
        
        protected void CollectCoin(GameCoin coin)
        {
            coinsCollected++;
            currentScore += 100 * currentLevel;
            playerFuel = Math.Min(100, playerFuel + 10);
            
            effects.Add(new GameEffect
            {
                X = coin.X,
                Y = coin.Y,
                Type = EffectType.CoinCollect,
                LifeTime = 0.8
            });
            
            // بررسی پایان مرحله
            if (coinsCollected >= 10 + currentLevel * 2)
            {
                CompleteLevel();
            }
        }
        
        protected void HandleEnemyCollision(GameEnemy enemy)
        {
            playerFuel -= 25;
            effects.Add(new GameEffect
            {
                X = enemy.X,
                Y = enemy.Y,
                Type = EffectType.Explosion,
                LifeTime = 1.0
            });
            enemies.Remove(enemy);
            
            if (playerFuel <= 0)
            {
                GameOver();
            }
        }
        
        protected void CompleteLevel()
        {
            gameRunning = false;
            showLevelComplete = true;
            currentLevel++;
            SaveGameData();
        }
        
        protected void GameOver()
        {
            gameRunning = false;
            showMainMenu = true;
            SaveGameData();
        }
        
        protected void NextLevel()
        {
            showLevelComplete = false;
            coinsCollected = 0;
            playerFuel = 100;
            gameRunning = true;
            GenerateCoins();
        }
        
        // سایر متدها...
    }
    
    // کلاس‌های کمکی
    public class GameCoin
    {
        public double X { get; set; }
        public double Y { get; set; }
        public int Value { get; set; }
        public bool IsCollected { get; set; }
    }
    
    public class GameEnemy
    {
        public double X { get; set; }
        public double Y { get; set; }
        public double SpeedX { get; set; }
        public double SpeedY { get; set; }
        public EnemyType Type { get; set; }
    }
    
    public class GameEffect
    {
        public double X { get; set; }
        public double Y { get; set; }
        public EffectType Type { get; set; }
        public double LifeTime { get; set; }
    }
    
    public enum EnemyType
    {
        Asteroid,
        UFO,
        SpaceShip,
        Boss
    }
    
    public enum EffectType
    {
        Explosion,
        CoinCollect,
        EngineTrail,
        Warp
    }
}
