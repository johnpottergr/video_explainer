#!/usr/bin/env node
/**
 * Render script for programmatic video generation.
 *
 * Usage:
 *   node scripts/render.mjs --props ./props.json --output ./output.mp4
 *   node scripts/render.mjs --composition StoryboardPlayer --props ./storyboard.json --output ./output.mp4
 *
 * The props.json file should contain the composition props.
 */

import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { createRequire } from "module";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";
import { readFileSync, existsSync } from "fs";

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  let propsPath = null;
  let outputPath = "./output.mp4";
  let compositionId = "ExplainerVideo";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--props" && args[i + 1]) {
      propsPath = args[i + 1];
      i++;
    } else if (args[i] === "--output" && args[i + 1]) {
      outputPath = args[i + 1];
      i++;
    } else if (args[i] === "--composition" && args[i + 1]) {
      compositionId = args[i + 1];
      i++;
    }
  }

  if (!propsPath) {
    console.error("Usage: node scripts/render.mjs [--composition <id>] --props <props.json> --output <output.mp4>");
    process.exit(1);
  }

  if (!existsSync(propsPath)) {
    console.error(`Props file not found: ${propsPath}`);
    process.exit(1);
  }

  // Load props from JSON file
  const props = JSON.parse(readFileSync(propsPath, "utf-8"));
  console.log(`Loaded props from ${propsPath}`);
  console.log(`Composition: ${compositionId}`);

  // Calculate total duration based on composition type
  let totalDuration;
  if (compositionId === "StoryboardPlayer" && props.storyboard) {
    totalDuration = props.storyboard.duration_seconds;
    console.log(`Storyboard: ${props.storyboard.title}`);
    console.log(`Beats: ${props.storyboard.beats.length}`);
  } else if (props.scenes) {
    totalDuration = props.scenes.reduce(
      (acc, scene) => acc + scene.durationInSeconds,
      0
    );
    console.log(`Title: ${props.title}`);
    console.log(`Scenes: ${props.scenes.length}`);
  } else {
    totalDuration = props.duration_seconds || 60;
  }
  console.log(`Total duration: ${totalDuration}s`);

  // Bundle the Remotion project
  console.log("\nBundling Remotion project...");
  const entryPoint = resolve(__dirname, "../src/index.ts");
  const bundleLocation = await bundle({
    entryPoint,
    onProgress: (progress) => {
      if (progress % 20 === 0) {
        console.log(`  Bundle progress: ${progress}%`);
      }
    },
  });

  console.log("Bundle created successfully");

  // Select the composition
  console.log("\nPreparing composition...");
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: compositionId,
    inputProps: props,
  });

  console.log(`Composition: ${composition.id}`);
  console.log(`Duration: ${composition.durationInFrames} frames @ ${composition.fps}fps`);
  console.log(`Resolution: ${composition.width}x${composition.height}`);

  // Render the video
  console.log(`\nRendering to ${outputPath}...`);
  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: outputPath,
    inputProps: props,
    onProgress: ({ progress }) => {
      const percent = Math.round(progress * 100);
      if (percent % 10 === 0) {
        process.stdout.write(`\r  Render progress: ${percent}%`);
      }
    },
  });

  console.log(`\n\nVideo rendered successfully: ${outputPath}`);
}

main().catch((err) => {
  console.error("Render failed:", err);
  process.exit(1);
});
