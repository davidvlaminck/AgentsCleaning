import json
from typing import Iterator

from EMInfraAPI.RequestHandler import RequestHandler
from EMInfraAPI.ResourceEnum import ResourceEnum
from EMInfraAPI.ResponseObject import ResponseObject
from EMInfraAPI.ZoekParameterOTL import ZoekParameterOTL


class EMInfraImporter:
    def __init__(self, request_handler: RequestHandler):
        self.request_handler = request_handler
        self.request_handler.requester.first_part_url += 'eminfra/'
        self.paging_cursors = {}

    def get_events_from_proxyfeed(self, resource: str, page_num: int = -1, page_size: int = 100) -> dict:
        if page_num == -1:
            url = f"feedproxy/feed/{resource}"
        else:
            url = f"feedproxy/feed/{resource}/{page_num}/{page_size}"
        response = self.request_handler.perform_get_request(url=url)
        decoded_string = response.content.decode("utf-8")
        return json.loads(decoded_string)

    def get_agents_from_oslo_search_endpoint_by_uuids(self, agent_uuids: [str]) -> Iterator[dict]:
        filter_dict = {'uuid': list(agent_uuids)}
        yield from self.get_objects_from_oslo_search_endpoint_with_iterator(resource=ResourceEnum.agents,
                                                                            filter_dict=filter_dict)

    def get_assets_from_oslo_search_endpoint_by_uuids(self, asset_uuids: [str]) -> Iterator[dict]:
        filter_dict = {'uuid': list(asset_uuids)}
        yield from self.get_objects_from_oslo_search_endpoint_with_iterator(resource=ResourceEnum.assets,
                                                                            filter_dict=filter_dict)

    def get_assetrelaties_from_oslo_search_endpoint_by_uuids(self, assetrelatie_uuids: [str]) -> Iterator[dict]:
        filter_dict = {'uuid': list(assetrelatie_uuids)}
        yield from self.get_objects_from_oslo_search_endpoint_with_iterator(resource=ResourceEnum.assetrelaties,
                                                                            filter_dict=filter_dict)

    def get_betrokkenerelaties_from_oslo_search_endpoint_by_uuids(self, betrokkenerelatie_uuids: [str]) -> Iterator[dict]:
        filter_dict = {'uuid': list(betrokkenerelatie_uuids)}
        yield from self.get_objects_from_oslo_search_endpoint_with_iterator(resource=ResourceEnum.betrokkenerelaties,
                                                                            filter_dict=filter_dict)

    def get_objects_from_oslo_search_endpoint_with_iterator(
            self, resource: ResourceEnum, cursor: str | None = None, size: int = 100,
            filter_dict: dict = None) -> Iterator[dict]:
        while True:
            response_object = self.get_objects_from_oslo_search_endpoint(resource=resource, cursor=cursor, size=size,
                                                                         filter_dict=filter_dict)
            yield from response_object.graph['@graph']
            if 'em-paging-next-cursor' not in response_object.headers:
                break
            cursor = response_object.headers['em-paging-next-cursor']

    def get_objects_from_oslo_search_endpoint(self, resource: ResourceEnum, cursor: str | None = None, size: int = 100,
                                              filter_dict: dict = None) -> ResponseObject:
        url = f'core/api/otl/{resource.value}/search'
        otl_zoekparameter = ZoekParameterOTL(size=size, from_cursor=cursor, filter_dict=filter_dict)

        if resource == ResourceEnum.agents:
            otl_zoekparameter.expansion_field_list = ['contactInfo']

        json_data = otl_zoekparameter.to_dict()

        response = self.request_handler.perform_post_request(url=url, json_data=json_data)

        decoded_string = response.content.decode("utf-8")
        return ResponseObject(graph=json.loads(decoded_string), headers=dict(response.headers))
