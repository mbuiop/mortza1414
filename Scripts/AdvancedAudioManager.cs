using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Audio;

public class AdvancedAudioManager : MonoBehaviour
{
    [Header("Audio Mixer")]
    public AudioMixer masterMixer;
    public AudioMixerGroup musicGroup;
    public AudioMixerGroup sfxGroup;
    public AudioMixerGroup uiGroup;

    [Header("Audio Sources")]
    public AudioSource backgroundMusic;
    public AudioSource soundEffects;
    public AudioSource uiSounds;
    public AudioSource ambientSpace;

    [Header("Advanced Audio Clips")]
    public AudioClip[] engineSounds;
    public AudioClip[] explosionSounds;
    public AudioClip[] weaponSounds;
    public AudioClip[] uiInteractionSounds;
    public AudioClip[] ambientSpaceSounds;

    [Header("Spatial Audio")]
    public float spatialBlend = 0.8f;
    public float dopplerLevel = 1.0f;
    public float spread = 90f;

    [Header("Dynamic Audio")]
    public AnimationCurve enginePitchCurve;
    public float maxEnginePitch = 1.5f;

    private Dictionary<string, AudioSource> audioPool = new Dictionary<string, AudioSource>();
    private float currentSpeed = 0f;

    public static AdvancedAudioManager Instance { get; private set; }

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
            InitializeAudioSystem();
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void InitializeAudioSystem()
    {
        SetupAudioMixer();
        CreateAudioPool();
        StartAmbientSounds();
    }

    void SetupAudioMixer()
    {
        // Configure advanced audio settings
        masterMixer.SetFloat("MusicVolume", 0f);
        masterMixer.SetFloat("SFXVolume", 0f);
        masterMixer.SetFloat("UIVolume", -5f);

        // Setup DSP effects
        masterMixer.SetFloat("MusicLowPass", 22000f);
        masterMixer.SetFloat("ReverbLevel", -10000f);
    }

    void CreateAudioPool()
    {
        // Create pooled audio sources for performance
        for (int i = 0; i < 10; i++)
        {
            GameObject audioObject = new GameObject($"AudioSource_{i}");
            audioObject.transform.SetParent(transform);
            
            AudioSource source = audioObject.AddComponent<AudioSource>();
            source.outputAudioMixerGroup = sfxGroup;
            source.spatialBlend = spatialBlend;
            source.dopplerLevel = dopplerLevel;
            source.spread = spread;
            source.playOnAwake = false;
            
            audioPool.Add($"PooledSource_{i}", source);
        }
    }

    void StartAmbientSounds()
    {
        if (ambientSpace != null && ambientSpaceSounds.Length > 0)
        {
            ambientSpace.clip = ambientSpaceSounds[Random.Range(0, ambientSpaceSounds.Length)];
            ambientSpace.loop = true;
            ambientSpace.Play();
        }
    }

    public void PlayBackgroundMusic()
    {
        if (backgroundMusic != null && !backgroundMusic.isPlaying)
        {
            backgroundMusic.loop = true;
            backgroundMusic.Play();
        }
    }

    public void PlayEngineSound(float speedNormalized)
    {
        currentSpeed = speedNormalized;
        
        // Dynamic engine sound based on speed
        float targetPitch = enginePitchCurve.Evaluate(speedNormalized) * maxEnginePitch;
        soundEffects.pitch = Mathf.Lerp(soundEffects.pitch, targetPitch, Time.deltaTime * 2f);

        if (!soundEffects.isPlaying && engineSounds.Length > 0)
        {
            soundEffects.clip = engineSounds[0];
            soundEffects.loop = true;
            soundEffects.Play();
        }
    }

    public void PlayExplosionSound(Vector3 position)
    {
        PlayPooledSound(explosionSounds, position, 1f);
        
        // Screen shake effect through audio
        StartCoroutine(ScreenShakeFromAudio(0.3f, 0.2f));
    }

    public void PlayWeaponSound(Vector3 position)
    {
        PlayPooledSound(weaponSounds, position, 0.7f);
    }

    public void PlayUISound()
    {
        if (uiInteractionSounds.Length > 0)
        {
            uiSounds.clip = uiInteractionSounds[Random.Range(0, uiInteractionSounds.Length)];
            uiSounds.Play();
        }
    }

    public void PlayCoinCollectSound(Vector3 position)
    {
        PlayPooledSound(uiInteractionSounds, position, 0.5f);
    }

    void PlayPooledSound(AudioClip[] clips, Vector3 position, float volume)
    {
        if (clips.Length == 0) return;

        // Find available audio source from pool
        AudioSource availableSource = null;
        foreach (var source in audioPool.Values)
        {
            if (!source.isPlaying)
            {
                availableSource = source;
                break;
            }
        }

        if (availableSource != null)
        {
            availableSource.transform.position = position;
            availableSource.clip = clips[Random.Range(0, clips.Length)];
            availableSource.volume = volume;
            availableSource.Play();
        }
    }

    IEnumerator ScreenShakeFromAudio(float duration, float magnitude)
    {
        // Audio-driven screen shake
        float elapsed = 0f;
        Vector3 originalPos = Camera.main.transform.localPosition;

        while (elapsed < duration)
        {
            float x = Random.Range(-1f, 1f) * magnitude;
            float y = Random.Range(-1f, 1f) * magnitude;

            Camera.main.transform.localPosition = new Vector3(x, y, originalPos.z);
            elapsed += Time.deltaTime;
            yield return null;
        }

        Camera.main.transform.localPosition = originalPos;
    }

    // Advanced audio effects
    public void SetLowPassFilter(float cutoffFrequency)
    {
        masterMixer.SetFloat("MusicLowPass", cutoffFrequency);
    }

    public void SetReverb(float reverbLevel)
    {
        masterMixer.SetFloat("ReverbLevel", reverbLevel);
    }

    public void FadeOutMusic(float duration)
    {
        StartCoroutine(FadeMixerGroup("MusicVolume", duration, -80f));
    }

    public void FadeInMusic(float duration)
    {
        StartCoroutine(FadeMixerGroup("MusicVolume", duration, 0f));
    }

    IEnumerator FadeMixerGroup(string exposedParam, float duration, float targetVolume)
    {
        float currentTime = 0f;
        float currentVol;
        masterMixer.GetFloat(exposedParam, out currentVol);
        currentVol = Mathf.Pow(10, currentVol / 20f);
        float targetValue = Mathf.Clamp(targetVolume, 0.0001f, 1f);

        while (currentTime < duration)
        {
            currentTime += Time.deltaTime;
            float newVol = Mathf.Lerp(currentVol, targetValue, currentTime / duration);
            masterMixer.SetFloat(exposedParam, Mathf.Log10(newVol) * 20f);
            yield return null;
        }
    }
}
