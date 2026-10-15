"""Neural decipherer v1: a small pretrained LM (Qwen2.5-0.5B, MLX) fine-tuned with LoRA to decipher.

Modules
  representation  relabelling-invariant cipher encoding (frequency-rank ids) + windowing + output vocabulary
  data            self-generated training/tuning tasks (tune/ref books, TRAIN families x TRAIN encodings only)
  model           MLX model wrapper: rank embeddings in, restricted character vocabulary out, batched generation
  reward          own copy of the scoring logic (char accuracy) + RL reward
  train_sft       supervised fine-tuning
  train_grpo      GRPO (group-relative policy gradient) from verifiable rewards
  predict         window aggregation, confidence calibration, wrapping into vcl.synthetic.schema.Prediction

Leakage rules (see reports/NEURAL_DECIPHERER.md): nothing in this package reads benchmark secrets, test-role books,
held-out language families, held-out encodings or decoy generators.
"""
