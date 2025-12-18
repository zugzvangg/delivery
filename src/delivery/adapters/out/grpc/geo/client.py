from grpclib.client import Channel

from src.delivery.adapters.out.grpc.geo import Contract_pb2
from src.delivery.adapters.out.grpc.geo.Contract_pb2_grpc import GeoStub
from src.delivery.core.domain.model.location.location import Location
from src.delivery.core.ports.geo_service import GeoServiceInterface


class GRPCGeoService(GeoServiceInterface):
    def __init__(self, host: str = "localhost", port: int = 5004):
        self._host = host
        self._port = port

    async def get_location(self, street: str) -> Location:
        async with Channel(self._host, self._port) as channel:
            stub = GeoStub(channel)
            request = Contract_pb2.GetGeolocationRequest(Street=street)
            response = await stub.GetGeolocation(request)
            loc = response.Location
            return Location(x=loc.x, y=loc.y)
