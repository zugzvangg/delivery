# from grpclib.client import Channel

import grpc

from src.delivery.adapters.out.grpc.geo.proto import Contract_pb2
from src.delivery.adapters.out.grpc.geo.proto.Contract_pb2_grpc import GeoStub
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.ports.geo_service import GeoServiceInterface


class GRPCGeoService(GeoServiceInterface):
    """
        GRPC-клиент для geo-сервиса.
        Использует один канал на весь сервис, работает через insecure_channel (HTTP/2 plaintext).
    """
    def __init__(self, host: str = "geo", port: int = 5004):
        self._address = f"{host}:{port}"
        self._channel = grpc.insecure_channel(self._address)
        self._stub = GeoStub(self._channel)

    def get_location(self, street: str) -> Location:
        """
        Получить координаты по названию улицы
        """
        request = Contract_pb2.GetGeolocationRequest(street=street)  # поле lowercase
        try:
            response = self._stub.GetGeolocation(request)
            loc = response.location  # snake_case!
            return Location(x=loc.x, y=loc.y)
        except grpc.RpcError as e:
            raise RuntimeError(f"gRPC error: {e.code()} {e.details()}") from e
