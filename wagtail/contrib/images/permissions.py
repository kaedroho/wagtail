from wagtail.permission_policies.collections import CollectionOwnershipPermissionPolicy
from wagtail.contrib.images import get_image_model
from wagtail.contrib.images.models import Image


permission_policy = CollectionOwnershipPermissionPolicy(
    get_image_model(),
    auth_model=Image,
    owner_field_name='uploaded_by_user'
)
