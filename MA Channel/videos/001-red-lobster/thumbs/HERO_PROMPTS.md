# 001 thumbnails: hero images

Save each image as a **PNG with a transparent background** in `thumbs/raw/` using the file name shown below. Then run:
```
python tools/thumbnails/make_thumb.py videos/001-red-lobster/thumbs/specs.json
```

Rules: no real people, no AI-made Red Lobster logos, and no fake documents with legible real names or numbers.

## T1 → `raw/T1_hero.png` (AI: ChatGPT image / gpt-image, set background to transparent)
> Photorealistic studio product shot. A tiny white plate holding three fried shrimp sits at the base of a towering, precarious stack of thick legal lease binders and paper documents, bound with black binder clips, several red "PAST DUE" rubber stamps on the paper edges. The stack is about ten times taller than the plate. Dramatic side lighting, deep shadows, slight low angle so the stack looms. Isolated object on a transparent background, no other text, no logos, no people. Vertical composition.

The point of the image is the scale: a small cost next to a huge one.

## T2 → `raw/T2_hero.png` (real photo, not AI)
1. Search Wikimedia Commons for "Red Lobster restaurant" and pick a clear, daytime photo of a storefront or exterior with the sign visible. Licence must be CC BY, CC BY-SA or public domain.
2. Record the author and licence in `thumbs/CREDITS.md` and add them to the credits line in the description.
3. Cut out the building (remove.bg, or Photoshop / Photopea "Remove background").
4. I'll add the "RENT DUE" notice as a paper overlay later, so don't create it with AI on the real photo.

## T3 → `raw/T3_hero.png` (AI)
> Photorealistic isolated photo of a generic single-story American casual-dining seafood restaurant building with a nautical look, weathered wood and a stone base, **no signage and no logos**. A huge brown paper price tag on a string hangs from the roof edge; the tag reads "SOLD $1.5B" in bold black marker. Soft daylight, three-quarter view. Transparent background, no people, no cars.

Check that the text on the tag came out correctly. If it didn't, regenerate with a blank tag and I'll add the text.

## Test plan
- YouTube Test & Compare: T1 vs T2 vs T3, all with title #1.
- Hypothesis: the number-contrast thumbnail (T1) wins on CTR. Log the result in STATE 7 days after publishing.
