using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

public class AdvancedEnemyController : MonoBehaviour
{
    [Header("AI Settings")]
    public Transform target;
    public float movementSpeed = 3f;
    public float rotationSpeed = 2f;
    public float attackRange = 8f;
    public float detectionRange = 12f;
    
    [Header("Advanced Behaviors")]
    public EnemyType enemyType;
    public AttackPattern attackPattern;
    public float aggression = 1f;
    
    [Header("Visual Effects")]
    public ParticleSystem engineTrail;
    public Light enemyGlow;
    public Renderer enemyRenderer;
    
    // AI variables
    private NavMeshAgent navAgent;
    private Rigidbody rb;
    private Vector3 currentDestination;
    private float attackCooldown = 0f;
    private int enemyLevel = 1;
    
    // Advanced behavior states
    private EnemyState currentState = EnemyState.Patrolling;
    private float stateTimer = 0f;
    private Vector3 patrolPoint;
    
    public enum EnemyType
    {
        Chaser,
        Shooter,
        Bomber,
        Defender
    }
    
    public enum AttackPattern
    {
        Direct,
        Surround,
        Wave,
        Ambush
    }
    
    public enum EnemyState
    {
        Patrolling,
        Chasing,
        Attacking,
        Evading
    }
    
    void Start()
    {
        navAgent = GetComponent<NavMeshAgent>();
        rb = GetComponent<Rigidbody>();
        
        InitializeEnemy();
        ChooseNewPatrolPoint();
    }
    
    void InitializeEnemy()
    {
        // Setup based on enemy type
        switch (enemyType)
        {
            case EnemyType.Chaser:
                movementSpeed = 4f;
                attackRange = 3f;
                break;
            case EnemyType.Shooter:
                movementSpeed = 2.5f;
                attackRange = 10f;
                break;
            case EnemyType.Bomber:
                movementSpeed = 3f;
                attackRange = 5f;
                break;
            case EnemyType.Defender:
                movementSpeed = 2f;
                attackRange = 6f;
                break;
        }
        
        // Visual customization
        CustomizeAppearance();
    }
    
    void CustomizeAppearance()
    {
        // Dynamic material and color based on type and level
        Color enemyColor = GetEnemyColor();
        enemyRenderer.material.color = enemyColor;
        enemyGlow.color = enemyColor;
        
        // Scale based on level
        float scale = 1f + (enemyLevel * 0.1f);
        transform.localScale = Vector3.one * scale;
    }
    
    Color GetEnemyColor()
    {
        switch (enemyType)
        {
            case EnemyType.Chaser: return Color.red;
            case EnemyType.Shooter: return Color.blue;
            case EnemyType.Bomber: return Color.yellow;
            case EnemyType.Defender: return Color.green;
            default: return Color.white;
        }
    }
    
    void Update()
    {
        if (target == null) return;
        
        UpdateStateMachine();
        UpdateCooldowns();
        UpdateVisualEffects();
    }
    
    void UpdateStateMachine()
    {
        float distanceToTarget = Vector3.Distance(transform.position, target.position);
        
        switch (currentState)
        {
            case EnemyState.Patrolling:
                HandlePatrollingState(distanceToTarget);
                break;
            case EnemyState.Chasing:
                HandleChasingState(distanceToTarget);
                break;
            case EnemyState.Attacking:
                HandleAttackingState(distanceToTarget);
                break;
            case EnemyState.Evading:
                HandleEvadingState(distanceToTarget);
                break;
        }
        
        stateTimer += Time.deltaTime;
    }
    
    void HandlePatrollingState(float distance)
    {
        // Patrol behavior
        if (stateTimer > 5f)
        {
            ChooseNewPatrolPoint();
            stateTimer = 0f;
        }
        
        MoveToPosition(patrolPoint);
        
        // Transition to chase if player is close
        if (distance < detectionRange)
        {
            currentState = EnemyState.Chasing;
            stateTimer = 0f;
        }
    }
    
    void HandleChasingState(float distance)
    {
        // Chase player
        MoveToPosition(target.position);
        
        // Transition to attack if in range
        if (distance < attackRange && attackCooldown <= 0f)
        {
            currentState = EnemyState.Attacking;
            stateTimer = 0f;
        }
        
        // Return to patrol if player escapes
        if (distance > detectionRange * 1.5f)
        {
            currentState = EnemyState.Patrolling;
            stateTimer = 0f;
        }
    }
    
    void HandleAttackingState(float distance)
    {
        // Execute attack based on type and pattern
        ExecuteAttack();
        
        // Cooldown period
        if (stateTimer > 2f)
        {
            currentState = EnemyState.Chasing;
            attackCooldown = 3f;
            stateTimer = 0f;
        }
    }
    
    void HandleEvadingState(float distance)
    {
        // Evasive maneuvers
        Vector3 evadeDirection = (transform.position - target.position).normalized;
        MoveToPosition(transform.position + evadeDirection * 5f);
        
        if (stateTimer > 3f)
        {
            currentState = EnemyState.Chasing;
            stateTimer = 0f;
        }
    }
    
    void ExecuteAttack()
    {
        switch (enemyType)
        {
            case EnemyType.Chaser:
                ExecuteChaserAttack();
                break;
            case EnemyType.Shooter:
                ExecuteShooterAttack();
                break;
            case EnemyType.Bomber:
                ExecuteBomberAttack();
                break;
            case EnemyType.Defender:
                ExecuteDefenderAttack();
                break;
        }
    }
    
    void ExecuteChaserAttack()
    {
        // Ram the player
        Vector3 chargeDirection = (target.position - transform.position).normalized;
        rb.AddForce(chargeDirection * 500f);
    }
    
    void ExecuteShooterAttack()
    {
        // Shoot projectiles
        // Implementation for projectile system
    }
    
    void ExecuteBomberAttack()
    {
        // Suicide bomb
        // Create explosion at position
    }
    
    void ExecuteDefenderAttack()
    {
        // Defensive attack pattern
    }
    
    void MoveToPosition(Vector3 position)
    {
        if (navAgent != null && navAgent.isActiveAndEnabled)
        {
            navAgent.SetDestination(position);
        }
        else
        {
            // Fallback movement
            Vector3 direction = (position - transform.position).normalized;
            transform.position += direction * movementSpeed * Time.deltaTime;
            
            // Smooth rotation
            if (direction != Vector3.zero)
            {
                Quaternion targetRotation = Quaternion.LookRotation(direction);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRotation, rotationSpeed * Time.deltaTime);
            }
        }
    }
    
    void ChooseNewPatrolPoint()
    {
        patrolPoint = transform.position + new Vector3(
            Random.Range(-10f, 10f),
            0,
            Random.Range(-10f, 10f)
        );
    }
    
    void UpdateCooldowns()
    {
        if (attackCooldown > 0f)
        {
            attackCooldown -= Time.deltaTime;
        }
    }
    
    void UpdateVisualEffects()
    {
        // Dynamic engine trail based on speed
        var emission = engineTrail.emission;
        emission.rateOverTime = rb.velocity.magnitude * 10f;
        
        // Pulsing glow effect
        float glowIntensity = 1f + Mathf.Sin(Time.time * 3f) * 0.3f;
        enemyGlow.intensity = glowIntensity;
    }
    
    public void SetLevelModifiers(int level)
    {
        enemyLevel = level;
        
        // Scale stats with level
        movementSpeed *= (1f + level * 0.1f);
        aggression *= (1f + level * 0.15f);
    }
    
    void OnDestroy()
    {
        // Death effects
        // Spawn explosion, drop loot, etc.
    }
}
