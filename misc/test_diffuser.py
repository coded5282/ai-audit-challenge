# Run this file from root to test inference the models.
#   python misc/test_diffuser.py
from diffusers import StableDiffusionPipeline

model_id = "CompVis/stable-diffusion-v1-1"
# model_id = "CompVis/stable-diffusion-v1-3"

with open(".hf_token", "r") as f:
    access_token = f.readline().strip()

# load model and scheduler
ldm = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=True)
modules = [ldm.unet, ldm.vae, ldm.text_encoder]
num_params = sum(
    param.numel() for module in modules for param in module.parameters()
)

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
