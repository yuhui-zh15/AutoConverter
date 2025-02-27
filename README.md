# Automated Generation of Challenging Multiple Choice Questions for Vision Language Model Evaluation

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![Pytorch](https://img.shields.io/badge/Pytorch-2.5-red.svg)](https://pytorch.org/get-started/previous-versions/#v25)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

This repo provides the PyTorch source code of our paper: [Automated Generation of Challenging Multiple Choice Questions for Vision Language Model Evaluation](https://arxiv.org/abs/2501.03225) (**CVPR 2025**). Check out project page [here](https://yuhui-zh15.github.io/AutoConverter-Website/)!

## 🔮 Abstract

The rapid development of vision language models (VLMs) demands rigorous and reliable evaluation. However, current visual question answering (VQA) benchmarks often depend on open-ended questions, making accurate evaluation difficult due to the variability in natural language responses. To address this, we introduce AutoConverter, an agentic framework that automatically converts these open-ended questions into multiple-choice format, enabling objective evaluation while reducing the costly question creation process. Our experiments demonstrate that AutoConverter can generate correct and challenging multiple-choice questions, with VLMs demonstrating consistently similar or lower accuracy on these questions compared to human-created ones. Using AutoConverter, we construct VMCBench, a benchmark created by transforming 20 existing VQA datasets into a unified multiple-choice format, totaling 9,018 questions. We comprehensively evaluate 28 state-of-the-art VLMs on VMCBench, setting a new standard for scalable, consistent, and reproducible VLM evaluation.

<img src="data/teaser.png"></img>
**Overview.** *(Left)* We analyze existing open-ended VQA evaluation metrics, underscoring their limitations in providing accurate and reproducible assessments. *(Middle)* We introduce AutoConverter, a multi-agent system that automatically converts open-ended questions into multiple-choice format, enabling objective assessment while reducing the costly question creation process. *(Right)* Using AutoConverter, we convert and refine 20 existing VQA datasets into a unified multiple-choice benchmark to support future VLM research.


## 🛠️ Method: AutoConverter

Check out [main.py](main.py) for the implementation of AutoConverter.

## 💎 Dataset: VMCBench

Dataset is available at [Huggingface](https://huggingface.co/datasets/suyc21/VMCBench).

## 🎯 Citation

If you use this repo in your research, please cite it as follows:
```
@inproceedings{AutoConverter,
  title={Automated Generation of Challenging Multiple-Choice Questions for Vision Language Model Evaluation},
  author={Yuhui Zhang and Yuchang Su and Yiming Liu and Xiaohan Wang and James Burgess and Elaine Sui and Chenyu Wang and Josiah Aklilu and Alejandro Lozano and Anjiang Wei and Ludwig Schmidt and Serena Yeung-Levy},
  booktitle={Conference on Computer Vision and Pattern Recognition (CVPR)},
  year={2025}
}
```
