using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using UnityEngine.SceneManagement;

public class GalaxyGameController : MonoBehaviour
{
    [Header("Player Settings")]
    public GameObject playerShip;
    public float playerSpeed = 15f;
    public float rotationSpeed = 5f;
    public int maxFuel = 100;
    
    [Header("Enemy Settings")]
    public GameObject[] enemyPrefabs;
    public int maxEnemies = 7;
    public float enemySpawnRate = 3f;
    
    [Header("Coin System")]
    public GameObject coinPrefab;
    public GameObject coinCollectEffect;
    public int coinsPerLevel = 20;
    
    [Header("UI Elements")]
    public TextMeshProUGUI scoreText;
    public TextMeshProUGUI fuelText;
    public TextMeshProUGUI levelText;
    public TextMeshProUGUI bombTimerText;
    public GameObject mainMenuPanel;
    public GameObject gamePanel;
    public GameObject levelCompletePanel;
    
    [Header("Advanced Effects")]
    public ParticleSystem warpSpeedEffect;
    public ParticleSystem explosionEffect;
    public Light directionalLight;
    public PostProcessVolume postProcessVolume;
    
    // Game state variables
    private int currentScore = 0;
    private int currentLevel = 1;
    private int currentFuel;
    private int coinsCollected = 0;
    private bool gameRunning = false;
    private float bombCooldown = 0f;
    private bool bombAvailable = true;
    
    // Advanced game systems
    private CinemachineVirtualCamera virtualCamera;
    private List<GameObject> activeEnemies = new List<GameObject>();
    private List<GameObject> activeCoins = new List<GameObject>();
    private Rigidbody playerRigidbody;
    
    // Touch controls
    private Vector2 joystickDirection = Vector2.zero;
    private bool isTouching = false;
    
    void Start()
    {
        InitializeGameSystems();
        ShowMainMenu();
        LoadPlayerData();
    }
    
    void InitializeGameSystems()
    {
        playerRigidbody = playerShip.GetComponent<Rigidbody>();
        virtualCamera = FindObjectOfType<CinemachineVirtualCamera>();
        currentFuel = maxFuel;
        
        // Setup advanced graphics
        SetupPostProcessing();
        SetupDynamicLighting();
    }
    
    void SetupPostProcessing()
    {
        // Configure cinematic post-processing
        var bloom = postProcessVolume.profile.GetSetting<Bloom>();
        bloom.intensity.value = 0.5f;
        bloom.threshold.value = 1.0f;
        
        var colorGrading = postProcessVolume.profile.GetSetting<ColorGrading>();
        colorGrading.postExposure.value = 0.1f;
        colorGrading.saturation.value = 10f;
    }
    
    void SetupDynamicLighting()
    {
        // Dynamic nebula lighting
        StartCoroutine(AnimateNebulaLights());
    }
    
    IEnumerator AnimateNebulaLights()
    {
        while (true)
        {
            float intensity = 1f + Mathf.Sin(Time.time * 0.5f) * 0.3f;
            directionalLight.intensity = intensity;
            
            // Rotate nebula colors
            float hue = Mathf.PingPong(Time.time * 0.1f, 1f);
            directionalLight.color = Color.HSVToRGB(hue, 0.3f, 1f);
            
            yield return new WaitForSeconds(0.1f);
        }
    }
    
    void Update()
    {
        if (!gameRunning) return;
        
        HandlePlayerInput();
        UpdateGameSystems();
        CheckCollisions();
        UpdateUI();
    }
    
    void HandlePlayerInput()
    {
        // Touch/Mouse input
        if (Input.GetMouseButton(0))
        {
            HandleTouchInput();
        }
        
        // Keyboard controls for testing
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        if (horizontal != 0 || vertical != 0)
        {
            Vector3 movement = new Vector3(horizontal, 0, vertical) * playerSpeed * Time.deltaTime;
            playerRigidbody.MovePosition(playerShip.transform.position + movement);
        }
        
        // Bomb activation
        if (Input.GetKeyDown(KeyCode.Space) && bombAvailable)
        {
            ActivateBomb();
        }
    }
    
    void HandleTouchInput()
    {
        // Advanced touch controls with acceleration
        Vector3 touchPosition = Input.mousePosition;
        Vector3 worldPosition = Camera.main.ScreenToWorldPoint(
            new Vector3(touchPosition.x, touchPosition.y, 10f));
        
        Vector3 direction = (worldPosition - playerShip.transform.position).normalized;
        Vector3 movement = direction * playerSpeed * Time.deltaTime;
        
        playerRigidbody.MovePosition(playerShip.transform.position + movement);
        
        // Smooth rotation towards movement direction
        if (direction != Vector3.zero)
        {
            Quaternion targetRotation = Quaternion.LookRotation(direction);
            playerShip.transform.rotation = Quaternion.Slerp(
                playerShip.transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
        }
    }
    
    void UpdateGameSystems()
    {
        UpdateFuelSystem();
        UpdateBombSystem();
        UpdateEnemySpawning();
        UpdateCameraEffects();
    }
    
    void UpdateFuelSystem()
    {
        // Fuel consumption based on movement
        currentFuel -= Mathf.RoundToInt(Time.deltaTime * 2f);
        currentFuel = Mathf.Clamp(currentFuel, 0, maxFuel);
        
        if (currentFuel <= 0)
        {
            GameOver();
        }
    }
    
    void UpdateBombSystem()
    {
        if (bombCooldown > 0)
        {
            bombCooldown -= Time.deltaTime;
            bombAvailable = false;
        }
        else
        {
            bombAvailable = true;
        }
    }
    
    void UpdateEnemySpawning()
    {
        if (activeEnemies.Count < maxEnemies && Random.Range(0f, 1f) < Time.deltaTime * enemySpawnRate)
        {
            SpawnAdvancedEnemy();
        }
    }
    
    void SpawnAdvancedEnemy()
    {
        GameObject enemyPrefab = enemyPrefabs[Random.Range(0, enemyPrefabs.Length)];
        Vector3 spawnPosition = GetRandomSpawnPosition();
        
        GameObject enemy = Instantiate(enemyPrefab, spawnPosition, Quaternion.identity);
        AdvancedEnemyController enemyController = enemy.GetComponent<AdvancedEnemyController>();
        
        // Configure enemy based on level
        enemyController.SetLevelModifiers(currentLevel);
        enemyController.target = playerShip.transform;
        
        activeEnemies.Add(enemy);
    }
    
    Vector3 GetRandomSpawnPosition()
    {
        // Spawn from edges of screen
        float spawnDistance = 15f;
        Vector3 spawnDirection = Random.onUnitSphere;
        spawnDirection.y = 0; // Keep on 2D plane
        
        return playerShip.transform.position + spawnDirection.normalized * spawnDistance;
    }
    
    void UpdateCameraEffects()
    {
        // Dynamic camera effects based on speed
        float speed = playerRigidbody.velocity.magnitude;
        virtualCamera.GetCinemachineComponent<CinemachineBasicMultiChannelPerlin>().m_AmplitudeGain = speed * 0.1f;
    }
    
    void CheckCollisions()
    {
        CheckCoinCollisions();
        CheckEnemyCollisions();
    }
    
    void CheckCoinCollisions()
    {
        for (int i = activeCoins.Count - 1; i >= 0; i--)
        {
            GameObject coin = activeCoins[i];
            if (coin == null) continue;
            
            float distance = Vector3.Distance(playerShip.transform.position, coin.transform.position);
            
            if (distance < 2f)
            {
                CollectCoin(coin);
                activeCoins.RemoveAt(i);
            }
        }
    }
    
    void CollectCoin(GameObject coin)
    {
        // Advanced collection effects
        Instantiate(coinCollectEffect, coin.transform.position, Quaternion.identity);
        
        coinsCollected++;
        currentScore += 10 * currentLevel;
        currentFuel = Mathf.Min(maxFuel, currentFuel + 15);
        
        // Audio feedback
        AudioManager.Instance.PlayCoinCollect();
        
        Destroy(coin);
        
        if (coinsCollected >= coinsPerLevel)
        {
            CompleteLevel();
        }
    }
    
    void CheckEnemyCollisions()
    {
        for (int i = activeEnemies.Count - 1; i >= 0; i--)
        {
            GameObject enemy = activeEnemies[i];
            if (enemy == null) continue;
            
            float distance = Vector3.Distance(playerShip.transform.position, enemy.transform.position);
            
            if (distance < 1.5f)
            {
                HandleEnemyCollision(enemy);
                activeEnemies.RemoveAt(i);
            }
        }
    }
    
    void HandleEnemyCollision(GameObject enemy)
    {
        // Cinematic explosion
        ParticleSystem explosion = Instantiate(explosionEffect, enemy.transform.position, Quaternion.identity);
        explosion.Play();
        
        // Screen shake
        StartCoroutine(ScreenShake(0.3f, 0.5f));
        
        // Damage player
        currentFuel -= 30;
        
        Destroy(enemy);
        Destroy(explosion.gameObject, 2f);
        
        if (currentFuel <= 0)
        {
            GameOver();
        }
    }
    
    IEnumerator ScreenShake(float duration, float magnitude)
    {
        Vector3 originalPos = virtualCamera.transform.localPosition;
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            float x = Random.Range(-1f, 1f) * magnitude;
            float y = Random.Range(-1f, 1f) * magnitude;
            
            virtualCamera.transform.localPosition = new Vector3(x, y, originalPos.z);
            
            elapsed += Time.deltaTime;
            yield return null;
        }
        
        virtualCamera.transform.localPosition = originalPos;
    }
    
    public void ActivateBomb()
    {
        if (!bombAvailable) return;
        
        bombCooldown = 10f;
        bombAvailable = false;
        
        // Destroy all enemies
        foreach (GameObject enemy in activeEnemies)
        {
            if (enemy != null)
            {
                Instantiate(explosionEffect, enemy.transform.position, Quaternion.identity);
                Destroy(enemy);
            }
        }
        activeEnemies.Clear();
        
        // Safe time period
        StartCoroutine(SafeTimePeriod());
    }
    
    IEnumerator SafeTimePeriod()
    {
        // Visual safe time indicator
        warpSpeedEffect.Play();
        
        yield return new WaitForSeconds(5f);
        
        warpSpeedEffect.Stop();
    }
    
    void CompleteLevel()
    {
        gameRunning = false;
        SavePlayerData();
        
        // Show level complete screen
        levelCompletePanel.SetActive(true);
        
        // Achievement check
        CheckAchievements();
    }
    
    void GameOver()
    {
        gameRunning = false;
        SavePlayerData();
        
        // Show game over screen
        ShowMainMenu();
    }
    
    // UI Management
    void UpdateUI()
    {
        scoreText.text = $"Score: {currentScore}";
        fuelText.text = $"Fuel: {currentFuel}%";
        levelText.text = $"Level: {currentLevel}";
        bombTimerText.text = bombAvailable ? "Bomb: READY!" : $"Bomb: {Mathf.Ceil(bombCooldown)}s";
    }
    
    // Button handlers
    public void StartGame()
    {
        mainMenuPanel.SetActive(false);
        gamePanel.SetActive(true);
        levelCompletePanel.SetActive(false);
        
        ResetGameState();
        gameRunning = true;
        
        // Start background music
        AudioManager.Instance.PlayBackgroundMusic();
    }
    
    public void NextLevel()
    {
        currentLevel++;
        coinsCollected = 0;
        levelCompletePanel.SetActive(false);
        
        GenerateNewCoins();
        gameRunning = true;
    }
    
    public void ShowMainMenu()
    {
        mainMenuPanel.SetActive(true);
        gamePanel.SetActive(false);
        levelCompletePanel.SetActive(false);
    }
    
    // Data management
    void SavePlayerData()
    {
        PlayerPrefs.SetInt("HighScore", Mathf.Max(currentScore, PlayerPrefs.GetInt("HighScore", 0)));
        PlayerPrefs.SetInt("HighLevel", Mathf.Max(currentLevel, PlayerPrefs.GetInt("HighLevel", 1)));
        PlayerPrefs.Save();
    }
    
    void LoadPlayerData()
    {
        // Load saved data
    }
    
    void CheckAchievements()
    {
        // Advanced achievement system
    }
    
    void ResetGameState()
    {
        currentScore = 0;
        currentLevel = 1;
        currentFuel = maxFuel;
        coinsCollected = 0;
        
        // Clear all objects
        foreach (GameObject obj in activeEnemies) Destroy(obj);
        foreach (GameObject obj in activeCoins) Destroy(obj);
        
        activeEnemies.Clear();
        activeCoins.Clear();
        
        // Reset player position
        playerShip.transform.position = Vector3.zero;
        
        // Generate initial coins
        GenerateNewCoins();
    }
    
    void GenerateNewCoins()
    {
        for (int i = 0; i < coinsPerLevel; i++)
        {
            Vector3 position = new Vector3(
                Random.Range(-10f, 10f),
                0,
                Random.Range(-10f, 10f)
            );
            
            GameObject coin = Instantiate(coinPrefab, position, Quaternion.identity);
            activeCoins.Add(coin);
        }
    }
}
