from app.infrastructure.redis.serializers import SerializerServices


def get_serializer_services() -> SerializerServices:
    return SerializerServices()
