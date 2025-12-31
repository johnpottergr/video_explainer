/**
 * Scene 17: Conclusion - The Full Picture
 *
 * Tie everything together with the complete optimization stack:
 * 1. Show the 40 → 3500+ journey
 * 2. List all techniques
 * 3. Key insight: memory-bound, not compute-bound
 * 4. These power every major AI service
 */

import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";

interface ConclusionSceneProps {
  startFrame?: number;
}

const COLORS = {
  background: "#0f0f1a",
  primary: "#00d9ff",
  success: "#00ff88",
  highlight: "#f1c40f",
  text: "#ffffff",
  textDim: "#888888",
  surface: "#1a1a2e",
};

const TECHNIQUES = [
  { name: "KV Caching", color: "#9b59b6", benefit: "Eliminates redundant computation" },
  { name: "Continuous Batching", color: "#00d9ff", benefit: "100% GPU utilization" },
  { name: "PagedAttention", color: "#00ff88", benefit: "95%+ memory efficiency" },
  { name: "Quantization", color: "#f1c40f", benefit: "4× smaller models" },
  { name: "Speculative Decoding", color: "#ff6b35", benefit: "2-3× faster latency" },
  { name: "Parallel Scaling", color: "#e74c3c", benefit: "Millions of users" },
];

export const ConclusionScene: React.FC<ConclusionSceneProps> = ({
  startFrame = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const localFrame = frame - startFrame;

  // Responsive scaling
  const scale = Math.min(width / 1920, height / 1080);

  // Phase timings
  const phase1End = fps * 5; // Speed comparison
  const phase2End = fps * 18; // Techniques list
  const phase3End = fps * 25; // Key insight
  const phase4End = fps * 30; // Final message

  // Speed counter animation
  const slowSpeed = interpolate(
    localFrame,
    [fps * 1, fps * 2],
    [0, 40],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const fastSpeed = interpolate(
    localFrame,
    [fps * 2, fps * 4],
    [40, 3500],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const speedMultiplier = Math.round(fastSpeed / Math.max(1, slowSpeed));

  // Animations
  const introOpacity = interpolate(localFrame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  const insightOpacity = interpolate(
    localFrame,
    [phase2End, phase2End + fps],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const finalOpacity = interpolate(
    localFrame,
    [phase3End, phase4End],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const finalScale = spring({
    frame: localFrame - phase3End,
    fps,
    config: { damping: 12, stiffness: 200 },
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.background,
        fontFamily: "Inter, sans-serif",
      }}
    >
      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 40 * scale,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: introOpacity,
        }}
      >
        <h1
          style={{
            fontSize: 48 * scale,
            fontWeight: 700,
            color: COLORS.text,
            margin: 0,
          }}
        >
          The Full Picture
        </h1>
      </div>

      {/* Main content */}
      <div
        style={{
          position: "absolute",
          top: 110 * scale,
          left: 80 * scale,
          right: 80 * scale,
          opacity: introOpacity,
        }}
      >
        {/* Speed comparison */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 40 * scale,
            marginBottom: 32 * scale,
          }}
        >
          {/* Naive */}
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 14 * scale, color: COLORS.textDim, marginBottom: 4 * scale }}>
              Naive Inference
            </div>
            <div
              style={{
                fontSize: 48 * scale,
                fontWeight: 700,
                fontFamily: "JetBrains Mono",
                color: "#ff4757",
              }}
            >
              {Math.round(slowSpeed)}
            </div>
            <div style={{ fontSize: 14 * scale, color: COLORS.textDim }}>tok/s</div>
          </div>

          {/* Arrow with multiplier */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 4 * scale,
            }}
          >
            <div style={{ fontSize: 32 * scale, color: COLORS.textDim }}>→</div>
            <div
              style={{
                padding: `${4 * scale}px ${12 * scale}px`,
                backgroundColor: COLORS.success + "20",
                borderRadius: 6 * scale,
                fontSize: 18 * scale,
                fontWeight: 700,
                color: COLORS.success,
              }}
            >
              {speedMultiplier}×
            </div>
          </div>

          {/* Optimized */}
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 14 * scale, color: COLORS.textDim, marginBottom: 4 * scale }}>
              Fully Optimized
            </div>
            <div
              style={{
                fontSize: 48 * scale,
                fontWeight: 700,
                fontFamily: "JetBrains Mono",
                color: COLORS.success,
              }}
            >
              {Math.round(fastSpeed).toLocaleString()}+
            </div>
            <div style={{ fontSize: 14 * scale, color: COLORS.textDim }}>tok/s</div>
          </div>
        </div>

        {/* Techniques grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 16 * scale,
            marginBottom: 32 * scale,
          }}
        >
          {TECHNIQUES.map((tech, index) => {
            const showAt = phase1End + index * (fps * 0.5);
            const techOpacity = interpolate(
              localFrame,
              [showAt, showAt + fps * 0.3],
              [0, 1],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            );

            return (
              <div
                key={tech.name}
                style={{
                  padding: 16 * scale,
                  backgroundColor: COLORS.surface,
                  borderRadius: 12 * scale,
                  border: `2px solid ${tech.color}`,
                  opacity: techOpacity,
                }}
              >
                <div
                  style={{
                    fontSize: 16 * scale,
                    fontWeight: 700,
                    color: tech.color,
                    marginBottom: 4 * scale,
                  }}
                >
                  {tech.name}
                </div>
                <div style={{ fontSize: 14 * scale, color: COLORS.textDim }}>
                  {tech.benefit}
                </div>
              </div>
            );
          })}
        </div>

        {/* Key insight box */}
        <div
          style={{
            padding: 24 * scale,
            backgroundColor: COLORS.highlight + "15",
            borderRadius: 16 * scale,
            border: `2px solid ${COLORS.highlight}`,
            textAlign: "center",
            marginBottom: 24 * scale,
            opacity: insightOpacity,
          }}
        >
          <div
            style={{
              fontSize: 20 * scale,
              fontWeight: 700,
              color: COLORS.highlight,
              marginBottom: 8 * scale,
            }}
          >
            The Key Insight
          </div>
          <div style={{ fontSize: 18 * scale, color: COLORS.text }}>
            LLM inference is{" "}
            <span style={{ color: COLORS.primary, fontWeight: 700 }}>
              memory-bound
            </span>
            , not compute-bound.
          </div>
          <div style={{ fontSize: 16 * scale, color: COLORS.textDim, marginTop: 8 * scale }}>
            Every optimization serves one goal: maximize useful work per byte
            transferred.
          </div>
        </div>
      </div>

      {/* Final message */}
      <div
        style={{
          position: "absolute",
          bottom: 80 * scale,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: finalOpacity,
          transform: `scale(${0.9 + finalScale * 0.1})`,
        }}
      >
        <div
          style={{
            display: "inline-block",
            backgroundColor: COLORS.success + "15",
            border: `3px solid ${COLORS.success}`,
            borderRadius: 16 * scale,
            padding: `${20 * scale}px ${40 * scale}px`,
          }}
        >
          <div
            style={{
              fontSize: 24 * scale,
              fontWeight: 700,
              color: COLORS.success,
            }}
          >
            These techniques power every major AI service today
          </div>
          <div
            style={{
              fontSize: 16 * scale,
              color: COLORS.textDim,
              marginTop: 8 * scale,
            }}
          >
            GPT-4 • Claude • Gemini • LLaMA • Mistral
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default ConclusionScene;
