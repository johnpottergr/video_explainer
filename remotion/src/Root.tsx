import { Composition } from "remotion";
import { ExplainerVideo } from "./scenes/ExplainerVideo";
import { defaultScriptProps, ScriptProps } from "./types/script";

/**
 * Root component that registers all compositions.
 * Each composition can be rendered independently.
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Main explainer video composition */}
      <Composition
        id="ExplainerVideo"
        component={ExplainerVideo}
        durationInFrames={30 * 180} // 180 seconds at 30fps (will be overridden by props)
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultScriptProps}
        calculateMetadata={async ({ props }) => {
          // Calculate duration from script
          const totalDuration = props.scenes.reduce(
            (acc, scene) => acc + scene.durationInSeconds,
            0
          );
          return {
            durationInFrames: Math.ceil(totalDuration * 30),
          };
        }}
      />
    </>
  );
};
