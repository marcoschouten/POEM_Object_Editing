from .config_sld_format import format_example
import json
import logging
from typing import Tuple, Dict, Any
import numpy as np
import os


def generate_sld_config(sample_dir: str, analysis_enhanced_file: str, user_edit_instruction: str) -> str:
    """Generate Stable Layout Diffusion configuration from enhanced analysis.

    Returns:
        str: Generated SLD configuration as a validated JSON string

    """
    try:
        # Load and validate input content
        with open(analysis_enhanced_file, "r") as file:
            content = file.read().strip()

        # Extract scene description
        scene_desc_lines = [line for line in content.split("\n") if "Scene Description:" in line]
        scene_description = scene_desc_lines[0].replace("Scene Description:", "").strip()

        # Extract objects and their bboxes
        objects = []
        current_object = {}
        content_lines = content.split("\n")
        for line in content_lines:
            if "Object " in line:
                if current_object:
                    objects.append(current_object)
                current_object = {}
            elif "Class:" in line and current_object is not None:
                current_object["class"] = line.split("Class:")[1].strip().lower()
            elif "Appearance Token:" in line and current_object is not None:
                current_object["appearance"] = line.split("Appearance Token:")[1].strip().lower()
            elif "Bounding Box (SLD format):" in line and "transformed" not in line:
                bbox_str = line.split("Bounding Box (SLD format):")[1].strip()
                current_object["sld_bbox"] = json.loads(bbox_str)
            elif "Bounding Box (SLD format) transformed:" in line:
                bbox_str = line.split("Bounding Box (SLD format) transformed:")[1].strip()
                current_object["transformed_bbox"] = json.loads(bbox_str)
        if current_object:
            objects.append(current_object)

        # Extract generation prompt and background description
        generation_prompt = None
        bg_prompt = None

        for i, line in enumerate(content_lines):
            if "Generation Prompt:" in line:
                # Get all lines until next section or end
                prompt_lines = []
                j = i + 1
                while (
                    j < len(content_lines)
                    and not content_lines[j].startswith("===")
                    and not any(x in content_lines[j] for x in ["Scene Description:", "Background Description:", "Spatial Relationships:", "Class:"])
                ):
                    if content_lines[j].strip():
                        prompt_lines.append(content_lines[j].strip())
                    j += 1
                generation_prompt = " ".join(prompt_lines)

            if "Background Description:" in line:
                # Get all lines until next section or end
                bg_lines = []
                j = i + 1
                while (
                    j < len(content_lines)
                    and not content_lines[j].startswith("===")
                    and not any(x in content_lines[j] for x in ["Scene Description:", "Generation Prompt:", "Spatial Relationships:", "Class:"])
                ):
                    if content_lines[j].strip():
                        bg_lines.append(content_lines[j].strip())
                    j += 1
                bg_prompt = " ".join(bg_lines)

        if not generation_prompt or not bg_prompt:
            raise ValueError("Could not extract generation prompt or background description")

        # Construct base config with all objects
        config_data = [
            {
                "input_fname": "input.png",
                "output_dir": os.path.basename(sample_dir),
                "prompt": user_edit_instruction,
                "generator": "dalle",
                "llm_parsed_prompt": {
                    "objects": [[obj["class"], [None]] for obj in objects],
                    "bg_prompt": bg_prompt,
                    "neg_prompt": "null",
                },
                "llm_layout_suggestions": [],
            }
        ]

        # Add layout suggestions with class-specific numbering
        layout_suggestions = []
        class_counts = {}

        for obj in objects:
            obj_class = obj["class"]
            appearance = obj.get("appearance", "")

            # Only combine appearance and class if appearance exists and is not "null"
            display_class = f"{appearance} {obj_class}" if appearance and appearance != "null" else obj_class

            # Increment count for this class
            class_counts[obj_class] = class_counts.get(obj_class, 0) + 1
            bbox = obj.get("transformed_bbox", obj["sld_bbox"])
            layout_suggestions.append([f"{display_class} #{class_counts[obj_class]}", bbox])

        config_data[0]["llm_layout_suggestions"] = layout_suggestions

        # Write validated config
        config_path = f"{sample_dir}/config_sld.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        logging.info(f"Successfully generated SLD config at {config_path}")
        return json.dumps(config_data)
    except Exception as e:
        logging.error(f"Error generating SLD config: {str(e)}")
        raise
