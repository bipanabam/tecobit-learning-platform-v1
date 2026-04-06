from helpers._cloudinary.services import get_cloudinary_video_object

def extract_youtube_id(url):
    import re
    pattern = r"(?:v=|youtu\.be/|embed/)([^&?/]+)"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_video_embed(instance):
    if instance.video_type == "youtube":
        video_id = extract_youtube_id(instance.video_url)
        
        if not video_id:
            return ""

        return f"""
        <iframe width="100%" height="100%"
        src="https://www.youtube.com/embed/{video_id}"
        title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
        </iframe>
        """

    elif instance.video_type == "cloudinary":
        return get_cloudinary_video_object(
            instance,
            field_name="video",
            as_html=True,
            width=750,
        )

    return ""