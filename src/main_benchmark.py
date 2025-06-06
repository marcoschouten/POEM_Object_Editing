import os
import sys
import logging
import argparse
import shutil
from typing import Optional
import subprocess
import time

from datasets import load_dataset

import cv2
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import configparser

# Custom utils imports
from utils_pose.models import Models
from utils_pose.open_cv_transformations import run_open_cv_transformations
from utils_pose.sam_refiner import run_sam_refine
from utils_pose.math_model import run_math_analysis
from utils_pose.vlm_image_parser import parse_image, save_results_image_parse
from utils_pose.sld_adapter import generate_sld_config

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"


def setup_logging() -> logging.Logger:
    """Configure and return logger"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return logging.getLogger(__name__)


def process_image(image_path: str, edit_type: str) -> Optional[cv2.Mat]:
    """
    Process image according to edit type

    Args:
        image_path: Path to input image
        edit_type: Type of edit to apply ('resize' or 'grayscale')

    Returns:
        Processed image or None if failed
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")

        if edit_type == "resize":
            return cv2.resize(image, (512, 512))
        elif edit_type == "grayscale":
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            return image

    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return None


def run_sld(
    json_path: str,
    input_path: str,
    output_dir: str,
    logger: logging.Logger,
    NORMAL_GPU: str,
    evaluation_folder_before: str,
    evaluation_folder_refined: str,
    save_file_name: str,
) -> None:
    """
    Run the SLD (Structure-aware Latent Diffusion) pipeline
    """
    # Path to the external script
    ext_script = "src/SLD/SLD_demo.py"
    config_ini = "/dtu/blackhole/14/189044/marscho/VLM_controller_for_SD/src/SLD/demo_config.ini"

    os.environ["CUDA_VISIBLE_DEVICES"] = NORMAL_GPU.replace("cuda:", "")

    evaluation_before_path = os.path.abspath(evaluation_folder_before)
    evaluation_refined_path = os.path.abspath(evaluation_folder_refined)
    subprocess.run(
        [
            "python",
            ext_script,
            "--json-file",
            json_path,
            "--input-dir",
            input_path,
            "--output-dir",
            output_dir,
            "--mode",
            "image_editing",
            "--config",
            config_ini,
            "--evaluation-path-before",
            evaluation_before_path,
            "--evaluation-path-refined",
            evaluation_refined_path,
            "--save-file-name",
            save_file_name,
        ]
    )


def main():
    """Main entry point of the program"""
    logger = setup_logging()

    # Check for CUDA availability and select device
    if torch.cuda.is_available():
        DEEP_SEEK_GPU = "cuda:1"  # Select CUDA device 1
        NORMAL_GPU = "cuda:0"  # Select CUDA device 2

    else:
        DEEP_SEEK_GPU = "cpu"
        NORMAL_GPU = "cpu"
    logger.info(f"Using device: {DEEP_SEEK_GPU}")

    # Initialize models
    models = Models(device_reasoning=NORMAL_GPU, DEEP_SEEK_GPU=DEEP_SEEK_GPU)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Process images with edit instructions")
    parser.add_argument("--in_dir", type=str, required=True, help="Directory containing input images")
    parser.add_argument("--out_dir", type=str, required=True, help="Directory for output files")
    parser.add_argument("--edit", type=str, choices=["resize", "grayscale", "none"], default="none", help="Edit instruction to apply to images")
    parser.add_argument("--draw", action="store_true", help="Enable drawing mode")
    parser.add_argument("--reasoning", action="store_true", help="Enable reasoning mode")
    parser.add_argument("--max_objects", type=int, default=5, help="Maximum number of objects allowed to be in an image")
    parser.add_argument("--dataset_size_samples", type=int, default=50, help="Number of samples to process")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.out_dir, exist_ok=True)

    # Create evaluation folders in the output directory
    evaluation_1_folder = os.path.join(args.out_dir, "evaluation_1_after_vlm")
    evaluation_2_folder = os.path.join(args.out_dir, "evaluation_2_after_sam")
    evaluation_3_folder = os.path.join(args.out_dir, "evaluation_3_after_llm_transformation")
    evaluation_4_folder = os.path.join(args.out_dir, "evaluation_4_after_sld")
    evaluation_5_folder = os.path.join(args.out_dir, "evaluation_5_after_sld_refine")
    os.makedirs(evaluation_1_folder, exist_ok=True)
    os.makedirs(evaluation_2_folder, exist_ok=True)
    os.makedirs(evaluation_3_folder, exist_ok=True)
    os.makedirs(evaluation_4_folder, exist_ok=True)
    os.makedirs(evaluation_5_folder, exist_ok=True)

    # CREATE DATASET FOLDER FOR BENCHMARK (instead of the INPUT_DEBUG)
    downloaddataset = False
    if downloaddataset:
        dataset = load_dataset("monurcan/precise_benchmark_for_object_level_image_editing", split="train")
        dataset = dataset.to_iterable_dataset()
        # dataset = dataset.take(args.dataset_size_samples)

        for sample in dataset:
            input_image, user_promppt, save_file_name = sample["input_image"], sample["edit_prompt"], sample["id"]
            input_mask = sample["input_mask"]

            subfolder_name = save_file_name
            # Create input subfolder for this sample
            sample_input_dir = os.path.join(args.in_dir, subfolder_name)
            os.makedirs(sample_input_dir, exist_ok=True)
            input_path = os.path.join(args.in_dir, subfolder_name, "input_image.png")
            edit_instruction_file = os.path.join(args.in_dir, subfolder_name, "edit_instruction.txt")
            with open(edit_instruction_file, "w") as file:
                file.write(user_promppt)
            input_image.save(input_path)
            input_mask.save(os.path.join(args.in_dir, subfolder_name, "input_mask.png"))
            # save the savefilename to a txt file
            with open(os.path.join(args.in_dir, subfolder_name, "save_file_name.txt"), "w") as file:
                file.write(save_file_name)

    # Load models
    vlm_model, vlm_processor = models.get_qwen_vlm()
    sam_model = models.get_sam()
    # math_model, math_tokenizer = models.get_qwen_math()
    math_model, math_tokenizer = models.get_deepseek_r1_text()

    # time computations and logging
    start_time = time.time()
    reasoning_time = 0
    drawing_time = 0
    sample_count = 0

    # Process each image in input directory
    for sample_idx, (subdir, _, files) in enumerate(os.walk(args.in_dir)):
        for filename in files:
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            # read the save_file_name.txt
            with open(os.path.join(subdir, "save_file_name.txt"), "r") as file:
                save_file_name = file.read().strip()

            sample_count += 1

            ## set paths
            input_path = os.path.join(subdir, filename)
            # Use the subfolder name from input dir as the output sample dir name
            subfolder_name = os.path.basename(subdir)
            sample_dir = os.path.join(args.out_dir, subfolder_name)
            os.makedirs(sample_dir, exist_ok=True)
            analysis_file = os.path.join(sample_dir, "analysis.txt")
            analysis_enhanced_file = os.path.join(sample_dir, "analysis_enhanced.txt")
            transformation_matrix_file = os.path.join(sample_dir, "transformation_matrix.npy")
            json_path = os.path.join(sample_dir, "config_sld.json")
            edit_instruction_file = os.path.join(subdir, "edit_instruction.txt")
            with open(edit_instruction_file, "r") as file:
                USER_EDIT = file.read().strip()

            logger.info(f"Processing sample #{sample_idx}: {input_path}")

            processed_image = process_image(input_path, args.edit)
            if processed_image is None:
                continue
            ### REASONING ###
            reasoning_start = time.time()
            if args.reasoning:
                #  STEP 1 VLM ---  parsing
                try:
                    results = parse_image(input_path, vlm_model, vlm_processor, NORMAL_GPU, USER_EDIT)
                    save_results_image_parse(sample_dir, processed_image, input_path, results)
                except:
                    print(f"No VLM parsing found for sample {sample_idx}")
                    continue
                VLM_BBOXES = results["objects"]
                if len(VLM_BBOXES) > args.max_objects:
                    print(f"Too many objects detected for sample {sample_idx}")
                    continue

                # Step 2: Refine detections with SAM
                logger.info(f"Refining detections for sample {sample_idx}")
                try:
                    SAM_MASKS = run_sam_refine(file_analysis_path=analysis_file, img_path=input_path, sam_model=sam_model)
                except:
                    print(f"No SAM masks found for sample {sample_idx}")
                    continue

                # Step 3:  LLM: Mathematical analysis
                logger.info(f"Performing mathematical analysis for sample {sample_idx}")
                try:
                    _, OBJECT_ID = run_math_analysis(
                        user_edit=USER_EDIT,  # Now using the read edit instruction specific to this sample
                        file_path=analysis_enhanced_file,
                        img_path=input_path,
                        model=math_model,
                        tokenizer=math_tokenizer,
                        device=DEEP_SEEK_GPU,
                    )
                except:
                    print(f"No math analysis found for object {OBJECT_ID}")
                    continue

                # Step 4: Apply transformations
                try:
                    TRANSFORMED_MASK = run_open_cv_transformations(
                        matrix_transform_file=transformation_matrix_file, output_dir=sample_dir, ENHANCED_FILE_DESCRIPTION=analysis_enhanced_file
                    )
                except:
                    print(f"No transformation matrix found for object {OBJECT_ID}")
                    # Create a black image with the same dimensions as the input image
                    TRANSFORMED_MASK = np.zeros_like(processed_image)
                    continue

                ### PREPARE FOR EVALUATION
                # SELECT THE CORRECT BBOX AND MASK
                try:
                    VLM_BBOX = VLM_BBOXES[OBJECT_ID - 1]["bbox"]
                except:
                    print(f"No bounding box found for object {OBJECT_ID}")
                    # Create a black mask with same dimensions as SAM_MASKS
                    VLM_BBOX = [0, 0, 1, 1]
                    continue

                try:
                    SAM_MASK = SAM_MASKS[str(OBJECT_ID)].astype(np.uint8) * 255
                except:
                    print(f"No SAM mask found for object {OBJECT_ID}")
                    # Create a black image with the same dimensions as the input image
                    SAM_MASK = np.zeros_like(processed_image)
                    continue

                # save the masks
                cv2.imwrite(os.path.join(evaluation_2_folder, f"{save_file_name}.png"), SAM_MASK)
                cv2.imwrite(os.path.join(evaluation_3_folder, f"{save_file_name}.png"), TRANSFORMED_MASK)
                # save the bboxes
                # Save VLM bbox as binary mask
                height, width = SAM_MASK.shape
                vlm_mask = np.zeros((height, width), dtype=np.uint8)
                xmin = int(VLM_BBOX[0] * width)
                ymin = int(VLM_BBOX[1] * height)
                xmax = int(VLM_BBOX[2] * width)
                ymax = int(VLM_BBOX[3] * height)
                vlm_mask[ymin:ymax, xmin:xmax] = 255
                cv2.imwrite(os.path.join(evaluation_1_folder, f"{save_file_name}.png"), vlm_mask)

            ### IMAGE GENERATION ###
            drawing_start = time.time()
            if args.draw:
                # Step 6: Generate config_sld.json for the SLD
                generate_sld_config(sample_dir, analysis_enhanced_file)
                # Step 7: Run SLD to generate edited image
                run_sld(
                    json_path=os.path.abspath(json_path),
                    input_path=os.path.abspath(input_path),
                    output_dir=os.path.abspath(sample_dir),
                    logger=logger,
                    NORMAL_GPU=NORMAL_GPU,
                    evaluation_folder_before=evaluation_4_folder,
                    evaluation_folder_refined=evaluation_5_folder,
                    save_file_name=save_file_name,
                )
            drawing_time += time.time() - drawing_start

    # time computations and logging
    end_time = time.time()
    total_time = end_time - start_time

    if sample_count > 0:
        avg_total_time = total_time / sample_count
        avg_reasoning_time = reasoning_time / sample_count if args.reasoning else 0
        avg_drawing_time = drawing_time / sample_count if args.draw else 0

        logger.info(f"Average processing time per sample: {avg_total_time:.2f} seconds")
        if args.reasoning:
            logger.info(f"Average reasoning time per sample: {avg_reasoning_time:.2f} seconds")
        if args.draw:
            logger.info(f"Average drawing time per sample: {avg_drawing_time:.2f} seconds")


if __name__ == "__main__":
    main()
