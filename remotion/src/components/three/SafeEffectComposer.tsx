/**
 * SafeEffectComposer - A wrapper for @react-three/postprocessing EffectComposer
 * that handles WebGL context issues during Remotion headless rendering.
 *
 * The issue: During long Remotion renders, WebGL contexts can become null or invalid.
 * When this happens, EffectComposer.addPass() fails with:
 * "Cannot read properties of null (reading 'alpha')"
 *
 * This wrapper checks if the WebGL context (gl) is available before rendering
 * the EffectComposer and its children.
 */

import React from "react";
import { useThree } from "@react-three/fiber";
import { EffectComposer } from "@react-three/postprocessing";

export interface SafeEffectComposerProps {
  children: React.ReactElement | React.ReactElement[];
}

/**
 * A safe wrapper for EffectComposer that prevents crashes when WebGL context is null.
 * Use this instead of importing EffectComposer directly from @react-three/postprocessing.
 *
 * @example
 * ```tsx
 * import { SafeEffectComposer } from "@remotion-components/three";
 *
 * const PostProcessing = () => (
 *   <SafeEffectComposer>
 *     <Bloom intensity={1.0} />
 *     <Vignette darkness={0.5} />
 *   </SafeEffectComposer>
 * );
 * ```
 */
export const SafeEffectComposer: React.FC<SafeEffectComposerProps> = ({ children }) => {
  const { gl } = useThree();

  // If the WebGL renderer is not available, don't render EffectComposer
  // This prevents "Cannot read properties of null (reading 'alpha')" errors
  if (!gl) {
    return null;
  }

  return <EffectComposer>{children}</EffectComposer>;
};

export default SafeEffectComposer;
