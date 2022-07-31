import requests
import pandas
from lxml import html
from functools import reduce
import sys

def get_metrics(metrics_session):
    # Get Metric Types
    url = "https://www.myfitnesspal.com/measurements/edit?page=1&type=1"
    data_result = metrics_session.get(url, headers=dict(referer=url))
    with open("C:\\Users\\Rober\\Downloads\\test_metrics.html", "wb") as f:
        f.write(data_result.content)
    tree = html.fromstring(data_result.content)
    print(f"tree: {tree}")
    metrics = tree.xpath("//select[@name='type']/option")
    print(metrics)
    all_metrics = []
    for single_metric in metrics:
        all_metrics.append(
            {
                "id": single_metric.xpath("./@value")[0],
                "name": single_metric.xpath("./text()")[0]
            }
        )
    return all_metrics


def get_data(data_metric):
    current_page = 1
    data_result_set = []
    # Loop until no more pages available
    while True:
        print(f"Getting data for {data_metric['name']} page {current_page}")
        # Request data from page
        url = f"https://www.myfitnesspal.com/measurements/edit?page={current_page}&type={data_metric['id']}"
        page_result = session.get(url, headers=dict(referer=url))
        tree = html.fromstring(page_result.content)
        # Extract values from the table containing the metrics
        data_table = tree.xpath("//table[@class='table0 check-in']/tbody/tr/td[@class='col-num']/text()")
        # Loop through data combining date/value pairs.
        table_length = len(data_table)
        current_table_position = 0
        while table_length > current_table_position:
            row_dict = {"date": str(data_table[current_table_position]),
                        data_metric['name']: str(data_table[current_table_position + 1])}
            data_result_set.append(row_dict)
            current_table_position += 2
        # This tells us if there is a next page or not
        if tree.xpath("//div[@class='pagination alt']/a[@class='next_page']"):
            current_page = current_page + 1
        else:
            break
    # Return result set as Pandas DataFrame
    return pandas.DataFrame.from_dict(data_result_set, orient="columns")


def write_data(input_data, output_file_name):
    # Write data out to disk as comma separated file
    input_data.to_csv(output_file_name, index=False)


if __name__ == "__main__":
    # Get required parameters from the user
    username = input("Enter MyFitnessPal UserName: ")
    password = input("Enter MyFitnessPal Password: ")
    output_file = input("Enter output file name: ")


    # Create Session
    with requests.session() as session:

        # Set Headers
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
            }
        )

        # Get login URL
        login_url = "https://www.myfitnesspal.com/account/login"
        login_result = session.get(login_url)

        # Get CSRF Token
        csrf_token_response = session.get("https://www.myfitnesspal.com/api/auth/csrf")
        csrf_token = session.get("https://www.myfitnesspal.com/api/auth/csrf").json()["csrfToken"]

        # Create payload for login
        payload = {
            "csrfToken": csrf_token,
            "username": username,
            "password": password,
            "redirect": False,
            "json": True
        }

        # Perform Login
        login_result = session.post(
            "https://www.myfitnesspal.com/api/auth/callback/credentials",
            data=payload
        )
        if "error=CredentialsSignin" in login_result.url:
            print("LOGIN FAILED")
            sys.exit(1)

        metrics_list = get_metrics(session)
        result_set = []
        # Iterate metric type, append to the result set
        for metric in metrics_list:
            print(f"Getting data for {metric['name']}")
            result_set.append(get_data(metric))

        # Merge result sets and output to disk
        combined_df = reduce(lambda x, y: pandas.merge(x, y, how="outer", on='date'), result_set)
        combined_df["date"] = pandas.to_datetime(combined_df.date)
        combined_df.sort_values(by=["date"], inplace=True)
        write_data(combined_df, output_file)
        print("Job Completed Successfully")
