# Run this file from root to test inference the models.
#   python misc/test_diffuser.py
from diffusers import DiffusionPipeline

# Other public options are `CompVis/ldm-text2im-large-256`, `CompVis/ldm-celebahq-256`
# Other private options are
#   `CompVis/stable-diffusion-v1-1-diffusers`
#   `CompVis/stable-diffusion-v1-2-diffusers`,
#   `CompVis/stable-diffusion-v1-3-diffusers`,
model_id = "CompVis/stable-diffusion-v1-3-diffusers"

# To use the stable diffusion private models
#   1. accept being invited into their CompVis org; details in email thread.
#   2. create access token here https://huggingface.co/settings/tokens
#   3. copy access token into ./.hf_token.
# The above steps are a must to use the really good models, since they aren't fully public!
with open(".hf_token", "r") as f:
    access_token = f.readline().strip()

# load model and scheduler
ldm = DiffusionPipeline.from_pretrained(model_id, use_auth_token=access_token)

# run pipeline in inference (sample random noise and denoise)
prompt = "A painting of a squirrel eating a burger"
images = ldm([prompt], num_inference_steps=50, eta=0.3, guidance_scale=6)["sample"]

# save images
for idx, image in enumerate(images):
    image.save(f"squirrel-{idx}.png")

prompt = "An astronaut eating hamburger in Texas"
images = ldm([prompt], num_inference_steps=50, eta=0.3, guidance_scale=6)["sample"]

# save images
for idx, image in enumerate(images):
    image.save(f"astronaut-{idx}.png")
