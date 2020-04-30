<script>
	import { onMount } from 'svelte';
	import Chart from 'chart.js';
	import 'chartjs-plugin-colorschemes';
	let trends = [];
	let userInput = "Fever, Sore throat, Shortness of breath, Loss of taste, Loss of smell";
	let myChart;
	let countries = [
		{ iso: 'US', text: "United States" },
		{ iso: 'SE', text: "Sweden" },
	]
	let selectedCountry;
	let casesUsa = [];
	let casesSweden = [];

	onMount(async () => {
		await updateAll();
	});

	async function updateAll() {
		await getTrends();
		if (selectedCountry.iso === 'US') {
			await getCovidCasesUSA();
		} else {
			await getCovidCasesSweden();
		}
		updateChart();
	}

	async function getTrends() {
		let body = {
			searchTerms: userInputToArray(),
			iso: selectedCountry.iso
		};
	    const response = await fetch('./api/trends', {
	    	method: 'POST',
			headers: {
				  'Content-Type': 'application/json'
				},
			body: JSON.stringify(body)
		});
	    const data = await response.json();
		trends = parseTrends(data);
	}

	function parseTrends(data) {
		const chartData = {};
		chartData["dates"] = [];
		chartData["searchTerms"] = [];
		for (const searchTerm in data) {
			if (searchTerm !== "isPartial") {
				if (chartData["dates"].length === 0) {
					for (const date in data[searchTerm]) {
						const dateObj = new Date(parseInt(date));
						const dateStr = dateToString(dateObj);
						chartData["dates"].push(dateStr);
					}
				}
				let searchTermData = {}
				searchTermData["name"] = searchTerm;
				searchTermData["values"] = [];
				for (const date in data[searchTerm]) {
					searchTermData["values"].push(data[searchTerm][date]);
				}
				chartData["searchTerms"].push(searchTermData);
			}
		}
		return chartData;
	}

	async function getCovidCasesUSA() {
		const response = await fetch('https://covidtracking.com/api/v1/us/daily.json');
	    const data = await response.json();
	    casesUsa = parseCasesUsa(data);
	}

	function parseCasesUsa(data) {
		let result = {};
		const numDaysTrend = trends["dates"].length;
		for (let row of data) {
			for (let [key, value] of Object.entries(row)) {
			  result[key] = result[key] || [];
			  result[key].unshift(value);
			}
		}
		for (let [key, value] of Object.entries(result)) {
			//line up start dates of cases and trends
			value.splice(0, value.length-numDaysTrend-2);
			//trim the 2 extra days of cases to line up end date with trends
			value.pop();
			value.pop();
		}
		return result;
	}

	async function getCovidCasesSweden() {
		const start_date = new Date("2020-01-22");
		const datesToFetch = [];
		for (let i = 0; i < daysBeween(start_date, new Date()); i++) {
			const nextDate = new Date("2020-01-22");
			nextDate.setDate(nextDate.getDate() + i);
			datesToFetch.push(dateToString(nextDate));
		}
		const responses = datesToFetch.map(date => getCovidCaseSweden(date));
		const newCases = []
		for await (const res of responses) {
			newCases.push(res["data"]);
		}
		casesSweden = parseCasesSweden(newCases);

	}

	async function getCovidCaseSweden(date) {
		let url = new URL('https://covid-api.com/api/reports');
		url.search = new URLSearchParams({
			date: date,
			iso: "SWE"
		});
		const response = await fetch(url);
		return await response.json();
	}

	function parseCasesSweden(data) {
		let result = {};
		result["dates"] = [];
		result["confirmed_diff"] = [];
		let manualDate = new Date("2020-01-25")
		const numDaysTrend = trends["dates"].length;
		for (let i = 0; i < 5; i++) {
			result["dates"].push(dateToString(manualDate));
			result["confirmed_diff"].push(0);
			manualDate.setDate(manualDate.getDate() + 1);
		}
		for (let row of data) {
			if (row.length > 0) {
				for (let [key, value] of Object.entries(row)) {
					result["dates"].push(value["date"]);
					result["confirmed_diff"].push(value["confirmed_diff"]);
				}
			}
		}
		console.log(result);
		return result;
	}



	function updateChart() {
		var ctx = document.getElementById('myChart').getContext('2d');
		const datasets = trends["searchTerms"].map(e => {
			return {
				label: e["name"],
				data: e["values"],
				fill: false,
				borderWidth: 3,
				pointRadius: 0,
				yAxisID: 'trend'
			}
		});
		if (selectedCountry.iso === 'US') {
			datasets.push({
				type: 'bar',
				label: "Daily New Cases USA",
				data: casesUsa["positiveIncrease"],
				fill: true,
				borderWidth: 0,
				pointRadius: 0,
				borderColor: 'rgba(252, 152, 3, 0.3)',
				backgroundColor: 'rgba(252, 152, 3, 0.3)',
				yAxisID: 'cases'
			});
		} else {
			datasets.push({
				type: 'bar',
				label: "Daily New Cases Sweden",
				data: casesSweden["confirmed_diff"],
				fill: true,
				borderWidth: 0,
				pointRadius: 0,
				borderColor: 'rgba(252, 152, 3, 0.3)',
				backgroundColor: 'rgba(252, 152, 3, 0.3)',
				yAxisID: 'cases'
			});
		}
		if (myChart) {
			myChart.destroy();
		}
		myChart = new Chart(ctx, {
			type: 'line',
			data: {
				labels: trends["dates"],
				datasets: datasets
			},
			options: {
				plugins: {
					colorschemes: {
						scheme: 'brewer.Paired5'
					}
				},
				scales: {
					yAxes: [{
						id: 'trend',
						position: 'left',
						ticks: {
							beginAtZero: true
						},
						gridLines: {
							color: "rgba(0, 0, 0, 0)",
						},
					},
					{
						id: 'cases',
						position: 'right',
						ticks: {
							beginAtZero: true,
							suggestedMax: selectedCountry.iso === 'US' ? 35000 : 1000 //Math.max(...casesUsa["positiveIncrease"])
						},
					}],
					xAxes: [{
						ticks: {
							userCallback: function (item, index) {
								if (!(index % 7)) return item;
							},
							autoSkip: false,
						},
						gridLines: {
							color: "rgba(0, 0, 0, 0)",
						},
					}]
				}
			}
		});
	}

	function userInputToArray() {
		return userInput.split(',').map(s => s.trim());
	}

	function dateToString(date) {
		// console.log(date);
		const year = date.getFullYear();
		const month = months[date.getMonth()];
		const day = ("0" + date.getDate()).slice(-2);
		return `${year}-${month}-${day}`;
	}

	function daysBeween(date1, date2) {
		return Math.floor((date2.getTime() - date1.getTime()) / (1000 * 3600 * 24));
	}

	const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

</script>

<main>
	<h1>Coronavirus Search Trends and Cases</h1>
	<select bind:value={selectedCountry}>
		{#each countries as country}
			<option value={country}>
				{country.text}
			</option>
		{/each}
	</select>
	<input bind:value={userInput}>
	<button on:click={updateAll}>Get trends</button>
	<div class="chart-container">
		<canvas id="myChart" width="400" height="200"></canvas>
	</div>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		margin: 0 auto;
	}

	h1 {
		font-size: 3em;
		font-weight: 100;
	}

	.chart-container {
		margin: 0 auto;
		position: relative;
		height:40vh;
		width:80vw
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}

	input {
		width: 30%;
	}
</style>