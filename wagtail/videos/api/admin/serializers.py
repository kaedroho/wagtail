from ..v2.serializers import VideoSerializer


class AdminVideoSerializer(VideoSerializer):
    thumbnail = VideoRenditionField("max-165x165", source="*", read_only=True)
