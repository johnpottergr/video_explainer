/**
 * SceneStoryboardPlayer - Data-driven scene renderer
 *
 * Renders a video from a storyboard.json file that references scene components
 * by type path (e.g., "llm-inference/hook").
 *
 * This approach allows:
 * - Scene components to be reused across projects
 * - Project-specific data (audio, timing) to live in project directories
 * - Easy creation of new videos by just creating new storyboard.json files
 */

import React from "react";
import {
  AbsoluteFill,
  Sequence,
  Audio,
  staticFile,
  useVideoConfig,
  interpolate,
  useCurrentFrame,
  Easing,
} from "remotion";
import { getSceneByPath } from "./index";

/**
 * SFX cue definition - frame-accurate sound effect trigger
 */
export interface SFXCue {
  /** Sound file name (without extension, looked up in sfx/ directory) */
  sound: string;
  /** Frame offset from scene start when sound should play */
  frame: number;
  /** Volume (0-1), defaults to 0.1 for subtle mix */
  volume?: number;
  /** Optional duration in frames (for looping sounds) */
  duration_frames?: number;
}

/**
 * Scene definition in storyboard.json
 */
export interface StoryboardScene {
  id: string;
  type: string; // e.g., "llm-inference/hook"
  title: string;
  audio_file: string;
  audio_duration_seconds: number;
  /** Frame-accurate SFX cues for this scene */
  sfx_cues?: SFXCue[];
}

/**
 * Video configuration
 */
export interface VideoConfig {
  width: number;
  height: number;
  fps: number;
}

/**
 * Style configuration
 */
export interface StyleConfig {
  background_color: string;
  primary_color: string;
  secondary_color: string;
  font_family: string;
}

/**
 * Background music configuration
 */
export interface BackgroundMusicConfig {
  /** Path to the music file (relative to public directory) */
  path: string;
  /** Volume level (0-1), defaults to 0.1 */
  volume?: number;
}

/**
 * Audio configuration
 */
export interface AudioConfig {
  voiceover_dir: string;
  buffer_between_scenes_seconds: number;
  /** Optional background music configuration */
  background_music?: BackgroundMusicConfig;
}

/**
 * Scene-based storyboard format
 */
export interface SceneStoryboard {
  title: string;
  description: string;
  version: string;
  project: string;
  video: VideoConfig;
  style: StyleConfig;
  scenes: StoryboardScene[];
  audio: AudioConfig;
  total_duration_seconds: number;
}

export interface SceneStoryboardPlayerProps {
  storyboard?: SceneStoryboard;
  /** Base path for voiceover files (for staticFile) */
  voiceoverBasePath?: string;
}

// Transition duration in seconds
const TRANSITION_DURATION = 0.7;

// Transition types for variety
type TransitionType = "fadeScale" | "slideLeft" | "slideRight" | "slideUp" | "zoomIn" | "wipe" | "crossfade";

const TRANSITION_TYPES: TransitionType[] = ["fadeScale", "slideLeft", "slideRight", "slideUp", "zoomIn", "wipe", "crossfade"];

// Deterministic "random" selection based on scene index (so it's consistent across renders)
const getTransitionType = (sceneIndex: number): TransitionType => {
  // Use a simple hash to pick transition type
  const hash = (sceneIndex * 7 + 3) % TRANSITION_TYPES.length;
  return TRANSITION_TYPES[hash];
};

/**
 * Dynamic transition component that varies based on scene index
 */
const SceneTransition: React.FC<{
  children: React.ReactNode;
  durationInFrames: number;
  sceneIndex: number;
}> = ({ children, durationInFrames, sceneIndex }) => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const transitionFrames = Math.floor(TRANSITION_DURATION * fps);
  const easing = Easing.out(Easing.cubic);
  const easingIn = Easing.in(Easing.cubic);

  const transitionType = getTransitionType(sceneIndex);

  // Common fade values
  const fadeIn = interpolate(frame, [0, transitionFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - transitionFrames, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: easingIn,
    }
  );

  const opacity = Math.min(fadeIn, fadeOut);
  const isInFadeOutPhase = frame > durationInFrames - transitionFrames;

  let transform = "";
  let filter = "";

  switch (transitionType) {
    case "fadeScale": {
      // Original fade + scale + translateY
      const scaleIn = interpolate(frame, [0, transitionFrames], [0.96, 1], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const scaleOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [1, 0.96], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const translateYIn = interpolate(frame, [0, transitionFrames], [-20, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const translateYOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, 20], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const scale = Math.min(scaleIn, scaleOut);
      const translateY = isInFadeOutPhase ? translateYOut : translateYIn;
      transform = `scale(${scale}) translateY(${translateY}px)`;
      break;
    }

    case "slideLeft": {
      // Slide in from right, slide out to left
      const slideIn = interpolate(frame, [0, transitionFrames], [100, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const slideOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, -100], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const translateX = isInFadeOutPhase ? slideOut : slideIn;
      transform = `translateX(${translateX}px)`;
      break;
    }

    case "slideRight": {
      // Slide in from left, slide out to right
      const slideIn = interpolate(frame, [0, transitionFrames], [-100, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const slideOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, 100], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const translateX = isInFadeOutPhase ? slideOut : slideIn;
      transform = `translateX(${translateX}px)`;
      break;
    }

    case "slideUp": {
      // Slide in from bottom, slide out to top
      const slideIn = interpolate(frame, [0, transitionFrames], [80, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const slideOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, -80], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const scaleIn = interpolate(frame, [0, transitionFrames], [0.98, 1], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const scaleOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [1, 0.98], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const translateY = isInFadeOutPhase ? slideOut : slideIn;
      const scale = Math.min(scaleIn, scaleOut);
      transform = `translateY(${translateY}px) scale(${scale})`;
      break;
    }

    case "zoomIn": {
      // Zoom in from larger, zoom out to smaller
      const scaleIn = interpolate(frame, [0, transitionFrames], [1.15, 1], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const scaleOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [1, 0.85], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const scale = isInFadeOutPhase ? scaleOut : scaleIn;
      transform = `scale(${scale})`;
      break;
    }

    case "wipe": {
      // Horizontal wipe with scale
      const clipIn = interpolate(frame, [0, transitionFrames], [100, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const clipOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, 100], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const scaleIn = interpolate(frame, [0, transitionFrames], [0.98, 1], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const scaleOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [1, 0.98], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const clip = isInFadeOutPhase ? clipOut : clipIn;
      const scale = Math.min(scaleIn, scaleOut);
      transform = `scale(${scale})`;
      // Use clip-path for wipe effect (handled via style below)
      break;
    }

    case "crossfade": {
      // Pure crossfade with slight blur
      const blurIn = interpolate(frame, [0, transitionFrames], [8, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
      });
      const blurOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, 8], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
      });
      const blur = isInFadeOutPhase ? blurOut : blurIn;
      filter = `blur(${blur}px)`;
      break;
    }
  }

  // Special handling for wipe transition clip-path
  let clipPath = "none";
  if (transitionType === "wipe") {
    const clipIn = interpolate(frame, [0, transitionFrames], [100, 0], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp", easing,
    });
    const clipOut = interpolate(frame, [durationInFrames - transitionFrames, durationInFrames], [0, 100], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easingIn,
    });
    const clip = isInFadeOutPhase ? clipOut : clipIn;
    clipPath = isInFadeOutPhase
      ? `inset(0 ${clip}% 0 0)`
      : `inset(0 0 0 ${clip}%)`;
  }

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity,
        transform: transform || "none",
        filter: filter || "none",
        clipPath,
        transformOrigin: "center center",
      }}
    >
      {children}
    </div>
  );
};

/**
 * Background music component with fade-in and fade-out effects
 * Plays throughout the entire video with looping support
 *
 * Wrapped in a Sequence to ensure proper timing across the full composition.
 */
const BackgroundMusic: React.FC<{
  musicPath: string;
  volume: number;
  totalDurationInFrames: number;
}> = ({ musicPath, volume, totalDurationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Fade-in: first 2 seconds
  const fadeInDurationFrames = 2 * fps;
  // Fade-out: last 3 seconds
  const fadeOutDurationFrames = 3 * fps;

  // Calculate fade-in volume (0 -> target volume over first 2 seconds)
  const fadeInVolume = interpolate(
    frame,
    [0, fadeInDurationFrames],
    [0, volume],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    }
  );

  // Calculate fade-out volume (target volume -> 0 over last 3 seconds)
  const fadeOutVolume = interpolate(
    frame,
    [totalDurationInFrames - fadeOutDurationFrames, totalDurationInFrames],
    [volume, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.in(Easing.cubic),
    }
  );

  // Combined volume: use fade-in at start, fade-out at end, full volume in between
  const currentVolume = Math.min(fadeInVolume, fadeOutVolume);

  return (
    <Sequence from={0} durationInFrames={totalDurationInFrames} name="Background Music">
      <Audio
        src={staticFile(musicPath)}
        volume={currentVolume}
        loop
      />
    </Sequence>
  );
};

/**
 * Fallback scene for missing components
 */
const MissingScene: React.FC<{ sceneType: string }> = ({ sceneType }) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#1a1a2e",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, sans-serif",
      }}
    >
      <div
        style={{
          fontSize: 48,
          fontWeight: 700,
          color: "#ff4757",
          marginBottom: 20,
        }}
      >
        Scene Not Found
      </div>
      <div
        style={{
          fontSize: 24,
          color: "#888",
        }}
      >
        Missing: {sceneType}
      </div>
    </AbsoluteFill>
  );
};

// Empty storyboard for fallback
const emptyStoryboard: SceneStoryboard = {
  title: "Empty",
  description: "",
  version: "2.0.0",
  project: "empty",
  video: { width: 1920, height: 1080, fps: 30 },
  style: {
    background_color: "#0f0f1a",
    primary_color: "#00d9ff",
    secondary_color: "#ff6b35",
    font_family: "Inter",
  },
  scenes: [],
  audio: { voiceover_dir: "voiceover", buffer_between_scenes_seconds: 1.0 },
  total_duration_seconds: 0,
};

export const SceneStoryboardPlayer: React.FC<SceneStoryboardPlayerProps> = ({
  storyboard = emptyStoryboard,
  voiceoverBasePath = "voiceover",
}) => {
  const { fps } = useVideoConfig();
  const buffer = storyboard.audio?.buffer_between_scenes_seconds ?? 1.0;

  // Calculate frame offsets for each scene
  let currentFrame = 0;
  const sceneData = storyboard.scenes.map((scene) => {
    const startFrame = currentFrame;
    // Scene duration = audio duration + buffer
    const durationSeconds = scene.audio_duration_seconds + buffer;
    const durationInFrames = Math.ceil(durationSeconds * fps);
    currentFrame += durationInFrames;

    // Look up scene component from registry
    const SceneComponent = getSceneByPath(scene.type);

    return {
      ...scene,
      startFrame,
      durationInFrames,
      durationSeconds,
      SceneComponent,
    };
  });

  // Calculate total duration for background music fade-out
  const totalDurationInFrames = currentFrame;

  // Background music configuration
  const backgroundMusic = storyboard.audio?.background_music;
  const musicVolume = backgroundMusic?.volume ?? 0.1;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: storyboard.style?.background_color || "#0f0f1a",
      }}
    >
      {/* Background music - plays throughout entire video with fade-in/fade-out */}
      {backgroundMusic?.path && (
        <BackgroundMusic
          musicPath={backgroundMusic.path}
          volume={musicVolume}
          totalDurationInFrames={totalDurationInFrames}
        />
      )}

      {sceneData.map((scene, index) => {
        const SceneComponent = scene.SceneComponent;
        const audioPath = `${voiceoverBasePath}/${scene.audio_file}`;

        return (
          <Sequence
            key={scene.id}
            from={scene.startFrame}
            durationInFrames={scene.durationInFrames}
            name={`Scene ${index + 1}: ${scene.title}`}
          >
            {/* Visual content with varied transitions */}
            <SceneTransition durationInFrames={scene.durationInFrames} sceneIndex={index}>
              {SceneComponent ? (
                <SceneComponent startFrame={0} />
              ) : (
                <MissingScene sceneType={scene.type} />
              )}
            </SceneTransition>

            {/* Voiceover/mixed audio track */}
            <Audio src={staticFile(audioPath)} volume={1} />

            {/* Frame-accurate SFX cues */}
            {scene.sfx_cues?.map((cue, cueIndex) => (
              <Sequence
                key={`sfx-${scene.id}-${cueIndex}`}
                from={cue.frame}
                durationInFrames={cue.duration_frames || 60}
                name={`SFX: ${cue.sound}`}
              >
                <Audio
                  src={staticFile(`sfx/${cue.sound}.wav`)}
                  volume={cue.volume ?? 0.1}
                />
              </Sequence>
            ))}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

/**
 * Calculate total duration from storyboard
 */
export function calculateStoryboardDuration(storyboard: SceneStoryboard): number {
  const buffer = storyboard.audio?.buffer_between_scenes_seconds ?? 1.0;
  return storyboard.scenes.reduce(
    (sum, scene) => sum + scene.audio_duration_seconds + buffer,
    0
  );
}

/**
 * Dynamic Storyboard Player - loads storyboard from build-time injection or props
 *
 * For dev preview: Uses storyboard injected at build time via webpack DefinePlugin
 * For rendering: Pass the storyboard prop directly to SceneStoryboardPlayer
 *
 * The storyboard is loaded from process.env.__STORYBOARD_JSON__ which is set
 * in remotion.config.ts based on the PROJECT environment variable.
 */

// Get build-time injected storyboard (set in remotion.config.ts)
const getInjectedStoryboard = (): SceneStoryboard | null => {
  try {
    // This is replaced at build time by webpack DefinePlugin
    const injected = process.env.__STORYBOARD_JSON__;
    if (injected && typeof injected === "object") {
      return injected as unknown as SceneStoryboard;
    }
    return null;
  } catch {
    return null;
  }
};

export const DynamicStoryboardPlayer: React.FC<SceneStoryboardPlayerProps> = ({
  storyboard: providedStoryboard,
  voiceoverBasePath = "voiceover",
}) => {
  // Priority: props > build-time injection
  const storyboard = providedStoryboard || getInjectedStoryboard();

  if (!storyboard) {
    return (
      <AbsoluteFill
        style={{
          backgroundColor: "#1a1a2e",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "Inter, sans-serif",
        }}
      >
        <div style={{ fontSize: 48, fontWeight: 700, color: "#ff4757", marginBottom: 20 }}>
          No Storyboard Found
        </div>
        <div style={{ fontSize: 24, color: "#888" }}>
          Make sure storyboard/storyboard.json exists in your project
        </div>
        <div style={{ fontSize: 18, color: "#666", marginTop: 20 }}>
          Run with: PROJECT=your-project npm run dev
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <SceneStoryboardPlayer
      storyboard={storyboard}
      voiceoverBasePath={voiceoverBasePath}
    />
  );
};

export default SceneStoryboardPlayer;
