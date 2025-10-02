import json
import pandas as pd
import requests
from typing import List, Dict, Optional
import os


# Simple functions can be imported and used in your code directly:
# from qzero_requests import simple_feature_request
# from qzero_requests import simple_report_request


def simple_feature_request(
    start_date: str, end_date: str, features: List[str], parse: bool = True
):
    """
    Requests feature data for a specified date range and features.

    Args:
        start_date (str): The start date of the request. Format: "YYYY-MM-DD".
        end_date (str): The end date of the request. Format: "YYYY-MM-DD".
        features (List[str]): A list of features to be requested.

    Returns:
        pd.DataFrame: A dataframe containing the requested feature data.
    """
    fv_request = FeatureRequest(start_date, end_date, features)
    meta_payload = MetaPayload([fv_request])
    base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
    endpoint = "/bulk/policies"
    client = QZeroClient(base_url, endpoint)
    if parse:
        return client.send_and_parse_meta(meta_payload)
    else:
        return client.send_meta(meta_payload)[0]


def simple_report_request(
    start_date: str,
    end_date: str,
    nodes: List[str],
    market: str,
    policies: List[str],
    features: List[str],
    summarize: bool,
):
    """
    Requests report data for a specified date range, nodes, market, policies, and features.

    Args:
        start_date (str): The start date of the request. Format: "YYYY-MM-DD".
        end_date (str): The end date of the request. Format: "YYYY-MM-DD".
        nodes (List[str]): A list of nodes to be requested.
        market (str): The market to be requested.
        policies (List[str]): A list of policies to be requested.
        features (List[str]): A list of features to be requested.
        summarize (bool): Whether to summarize the data.
    """
    base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
    endpoint = "/report"
    client = QZeroClient(base_url, endpoint)
    form = {
        "from_date": start_date,
        "to_date": end_date,
        "nodes": json.dumps(nodes),
        "market": market,
        "policies": json.dumps(policies),
        "features": json.dumps(features),
        "summarize": str(summarize).lower(),
    }
    return client.send_form(form)


def simple_request_entities(entity_type: str, limit: Optional[int] = None):
    """
    Requests available entities from Quantum Zero.

    Returns:
        requests.Response: The response from the API.
    """
    base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
    endpoint = f"/{entity_type}/list"
    params = "" if not limit else "?limit=" + str(limit)
    client = QZeroClient(base_url, endpoint, params)
    return client.request_entities().json()


def simple_request_entity_by_name(entity_type: str, name: str):
    """
    Requests available entities from Quantum Zero.

    Args:
        name (str): The name of the entity to be requested.

    Returns:
        requests.Response: The response from the API.
    """
    base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
    endpoint = f"/{entity_type}/name/{name}"
    client = QZeroClient(base_url, endpoint)
    return client.request_entities().json()

class ExampleFeatureRequest:
    def __init__(self):
        base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
        endpoint = "/bulk/policies"
        self.client = QZeroClient(base_url, endpoint)

    def request_features(self) -> List[pd.DataFrame]:
        """
        Requests feature data for specified date ranges and features.

        This function creates a list of feature requests, each specifying a date range and a list of features to be requested.
        It then sends these requests to Quantum Zero and parses the responses into dataframes.

        Returns:
            list of pd.DataFrame: A list of dataframes, each corresponding to a feature request.
        """
        fv_requests = [
            FeatureRequest(
                start_date="2024-10-14",
                end_date="2024-10-16",
                features=[
                    "pjm_fuel_coal_mw",
                    "pjm_fuel_gas_mw",
                    "pjm_fuel_hydro_mw",
                    "pjm_fuel_multiple_fuels_mw",
                    "pjm_fuel_nuclear_mw",
                    "pjm_fuel_oil_mw",
                    "pjm_fuel_other_renewables_mw",
                    "pjm_fuel_solar_mw",
                    "pjm_fuel_storage_mw",
                    "pjm_fuel_wind_mw",
                    "pjm_load_total_mw",
                ],
            ),
            # You can modify the request above, or add more requests below:
            # FeatureRequest(
            #    etc
            # )
        ]
        meta_payload = MetaPayload(fv_requests)
        dataframes = self.client.send_and_parse_meta(meta_payload)

        return dataframes

    def main(self):
        dataframes = self.request_features()
        for dataframe in dataframes:
            print(pd.concat((dataframe.head(3), dataframe.tail(3))))


class ExampleReportRequest:
    def __init__(self):
        base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
        endpoint = "/report"
        self.client = QZeroClient(base_url, endpoint)

    def request_report(self) -> requests.Response:
        """
        Requests report data for specified date ranges, nodes, market, policies, and features.

        This function sends a report request to Quantum Zero and returns the response.

        Returns:
            requests.Response: The response from the API.
        """
        form = {
            "from_date": "2024-10-14",
            "to_date": "2024-10-16",
            "nodes": json.dumps(["MISO"]),
            "market": "PJMvirts",
            "policies": json.dumps(["PJMvirts Pricetaker Long"]),
            "features": json.dumps(
                [
                    "pjm_fuel_coal_mw",
                    "pjm_fuel_gas_mw",
                    "pjm_fuel_hydro_mw",
                    "pjm_fuel_multiple_fuels_mw",
                    "pjm_fuel_nuclear_mw",
                    "pjm_fuel_oil_mw",
                    "pjm_fuel_other_renewables_mw",
                    "pjm_fuel_solar_mw",
                    "pjm_fuel_storage_mw",
                    "pjm_fuel_wind_mw",
                    "pjm_load_total_mw",
                ]
            ),
            "summarize": "false",
        }
        response = self.client.send_form(form)
        return response

    def main(self):
        response = self.request_report()
        print(response.json())


class ExampleRequestEntity:
    def __init__(self):
        base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
        endpoint = "/scraper/name/PJMvirts DA"
        self.client = QZeroClient(base_url, endpoint)

    def request_entities(self) -> requests.Response:
        """
        Requests available entities from Quantum Zero.

        This function sends a request for available entities to Quantum Zero and returns the response.

        Returns:
            requests.Response: The response from the API.
        """
        response = self.client.request_entities()
        return response

    def main(self):
        response = self.request_entities()
        print(response.json())

class ExampleRequestEntities:
    def __init__(self):
        base_url = "https://quantum-zero-dev-eu8cy.ondigitalocean.app"
        endpoint = "/scraper/list"
        self.client = QZeroClient(base_url, endpoint)

    def request_entities(self) -> requests.Response:
        """
        Requests available entities from Quantum Zero.

        This function sends a request for available entities to Quantum Zero and returns the response.

        Returns:
            requests.Response: The response from the API.
        """
        response = self.client.request_entities()
        return response

    def main(self):
        response = self.request_entities()
        print(response.json())

## Helper functions below, feel free to ignore
class FeatureRequest:
    """
    A class representing a feature request.

    Args:
        start_date (str): The start date of the request. Format: "YYYY-MM-DD".
        end_date (str): The end date of the request. Format: "YYYY-MM-DD".
        features (List[str]): A list of features to be requested.
    """

    def __init__(self, start_date: str, end_date: str, features: List[str]):
        self.start_date = start_date
        self.end_date = end_date
        self.features = features

    def to_dict(self) -> Dict[str, List[str]]:
        datetimes = pd.date_range(
            start=self.start_date,
            end=pd.to_datetime(self.end_date) + pd.Timedelta(hours=23),
            freq="h",
        )
        datetimes_as_string = [
            datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
            for datetime in datetimes.tz_localize("EST")
        ]
        fv_request = {
            "index": datetimes_as_string,
            "features": self.features,
        }
        return fv_request


class MetaPayload:
    """
    A class representing a meta payload for sending feature requests.

    Args:
        fv_requests (List[FeatureRequest]): A list of feature requests.
    """

    def __init__(self, fv_requests: List[FeatureRequest]):
        self.source = os.path.basename(__file__)
        self.input = None
        self.payload_type = "vecfvrequests"
        self.hash = None
        self.json = json.dumps([fv_request.to_dict() for fv_request in fv_requests])

    def to_dict(self) -> Dict[str, str]:
        return {
            "source": self.source,
            "input": self.input,
            "payload_type": self.payload_type,
            "hash": self.hash,
            "json": self.json,
        }


class QZeroClient:
    def __init__(self, base_url: str, endpoint: str, params: str = ""):
        self.base_url = base_url
        self.endpoint = endpoint
        self.url = f"{self.base_url}{self.endpoint}{params}"

    def send_meta(self, meta_payload: MetaPayload) -> requests.Response:
        """
        Sends a POST request to the Quantum Zero API.

        Args:
            meta_payload (MetaPayload): The payload to be sent.

        Returns:
            requests.Response: The response from the API.
        """
        response = requests.post(
            self.url,
            json=meta_payload.to_dict(),
        )
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
        return response

    def parse_response(self, response: requests.Response) -> List[pd.DataFrame]:
        """
        Parses the response from the Quantum Zero API into a list of dataframes

        Args:
            response (requests.Response): The response from the API.

        Returns:
            list of pd.DataFrame: A list of dataframes, each corresponding to a feature request.
        """
        fvresponses = response.json()["data"]
        dataframes = []
        for fvresponse in fvresponses:
            features = fvresponse["features"]
            df = pd.DataFrame()
            for feature in features:
                feature_name = feature["name"]
                feature_values = feature["values"]
                df_feature = pd.DataFrame(feature_values)
                if "datetime" not in df_feature.columns:
                    continue
                df_feature["datetime"] = pd.to_datetime(df_feature["datetime"])
                df_feature = df_feature.set_index("datetime")
                df_feature = df_feature.drop(
                    columns=[
                        "id",
                        "feature_id",
                        "time_recorded",
                        "published_at",
                        "updated_at",
                    ]
                )
                df_feature = df_feature.rename(columns={"value": feature_name})
                df = pd.concat([df, df_feature], axis=1)
            dataframes.append(df)
        return dataframes

    def send_and_parse_meta(self, meta_payload: MetaPayload) -> List[pd.DataFrame]:
        """
        Sends a request to the Quantum Zero API and parses the response into a list of dataframes.

        Args:
            meta_payload (MetaPayload): The payload to be sent.

        Returns:
            list of pd.DataFrame: A list of dataframes, each corresponding to a feature request.
        """
        response = self.send_meta(meta_payload)
        dataframes = self.parse_response(response)
        return dataframes

    def send_form(self, form: dict) -> requests.Response:
        response = requests.post(self.url, data=form)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
        return response

    def request_entities(self) -> requests.Response:
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)
        return response


if __name__ == "__main__":
    # ExampleFeatureRequest().main()
    # ExampleReportRequest().main()
    # ExampleRequestEntities().main()
    # ExampleRequestEntity().main()
    print("Check the examples to see how to use the functions.")