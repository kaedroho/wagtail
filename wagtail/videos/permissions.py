from wagtail.core.permission_policies.collections import (
    CollectionOwnershipPermissionPolicy,
)
from wagtail.videos import get_video_model
from wagtail.videos.models import Video

permission_policy = CollectionOwnershipPermissionPolicy(
    get_video_model(), auth_model=Video, owner_field_name="uploaded_by_user"
)
