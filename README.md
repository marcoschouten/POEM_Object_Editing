# 📜 POEM: Precise Object-level Editing via MLLM control

Please refer to our paper for details: "[📜 POEM: Precise Object-level Editing via MLLM control](https://poem.compute.dtu.dk/)", SCIA 2025.

This project aims to allow **image editing via precise instructions** (e.g. move cat to the left by 12.5 px). Our method synthesizes a new image according to the editing instruction. We do this using off-the-shelf diffusion models and MLLMs with no training or fine-tuning.

<p>
  <img src="./docs/fig_method.png" alt="method" width="100%"/>
</p>
<p><i><b>Pipeline Description:</b> Given an image and an edit prompt, we first
use an MLLM to analyze the scene and identify objects. Then, we refine the detections
and enhance object masks using Grounded SAM. Next, we use a text-based LLM
to predict the transformation matrix of the initial segmentation mask. Finally, we
perform an image-to-image translation guided by the previous steps to generate the
edited image. This structured pipeline enables precise object-level editing with high
visual fidelity while preserving spatial and visual coherence.</i></p>

## 📦 Installation
### Virtual Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
./scripts/install_packages.sh
```
**Note:** The LLM **DeepseekR1-32GB** requires ~74GB VRAM.

**Dependencies:**
- **SAM2**: `python>=3.10`, `torch>=2.5.1`, `torchvision>=0.20.1`
- **QWEN-Math**: `transformers>=4.37.0`

## ⚙️ Usage

### Run Pipeline
```bash
python src/main.py --in_dir input_debug --out_dir output_debug --edit "grayscale"
```

## 📊 Results

![masks](./docs/fig_results.png)
We compare POEM to state-of-the-art image editing
models. We test our edit instructions using translation, scaling, appearance changing,
and a combination of them to showcase the precision of our pipeline.



## 📚 Citation
Please cite the following paper when using the code or data:
```
@inproceedings{schouten2025poem,
    title={POEM: Precise Object-level Editing via MLLM control},
    author={Schouten, Marco and Kaya, Mehmet Onurcan and Belongie, Serge and Papadopoulos, Dim P.},
    booktitle={Scandinavian Conference on Image Analysis},
    year={2025},
}
```



