$(document).ready(function () {
    // Fetch filter options for facilities, provinces, districts, and counties
    fetch('/api/facilities')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Populate facility filter dropdown
        populateSelectOptions('#facilityFilter', data.facilities, 'facility_id', 'facility_name');
        // Populate province filter dropdown
        populateSelectOptions('#provinceFilter', data.provinces);
        // Populate district filter dropdown
        populateSelectOptions('#districtFilter', data.districts);
        // Populate county filter dropdown
        populateSelectOptions('#countyFilter', data.counties);
    })
    .catch(error => {
        console.error('Error fetching filter options:', error);
    });

function populateSelectOptions(selector, optionsData, valueField = null, textField = null) {
    var select = $(selector);
    select.empty();
    //Add option for None as the default option
    select.append($('<option></option>').attr('value', '').text('------'));
    $.each(optionsData, function (index, option) {
        var value = valueField ? option[valueField] : option;
        var text = textField ? option[textField] : option;
        select.append($('<option></option>').attr('value', value).text(text));
    });
}

// Event listener for filter change
// Event listener for Apply Filter button click
$('#applyFilterForm').submit(function (event) {
    event.preventDefault(); // Prevent default form submission behavior
    // Fetch data and render graphs based on selected filters
    fetchDataAndRenderGraphs();
});
function fetchDataAndRenderGraphs(group_by){
    //banner
    var graphBanner= $('#graph_banner');
    console.log(graphBanner)
    //define filters
    var province = $('#provinceFilter').val()?$('#provinceFilter').val():'';
    var county = $('#countyFilter').val()?$('#countyFilter').val():'';
    var district = $('#districtFilter').val()?$('#districtFilter').val():'';
    var facility = $('#facilityFilter').val()?$('#facilityFilter').val():'';
    var orgLevel ='';
    if(province !=''){
        orgLevel+=`For ${province} Province,`;
    }
    if(county !=''){
        orgLevel+=`${county} County,`;
    }
    if(district !=''){
        orgLevel+=`${district} District`;
    }
    //fetch stats
    fetch(`/api/analytics-overview?province=${province}&county=${county}&district=${district}&facility_id=${facility}`)
        .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
        })
        .then(data => {
        if(data.length==0){
            graphBanner.removeClass("d-none")
        }
        // Update card values with fetched data
        $('#totalFacilities').text(Intl.NumberFormat().format(data.total_facilities));
        $('#totalPatients').text(Intl.NumberFormat().format(data.total_patients));
        $('#totalInitialVisits').text(Intl.NumberFormat().format(data.total_initial_visits));
        $('#totalFollowupVisits').text(Intl.NumberFormat().format(data.total_followup_visits));

        // Fetch BP control analytics
        fetchBpControlAnalytics();
        })
        .catch(error => {
        console.error('Error fetching data:', error);
        });
    //fetch bp analytics
    fetch(`/api/bpcontrol-analytics?province=${province}&county=${county}&district=${district}&facility_id=${facility}&group_by=${group_by}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if(data.length==0){
                graphBanner.removeClass("d-none")
            }
        BpControlchart(data,orgLevel);
        BpMedsControlchart(data,orgLevel);
        })
        .catch(error => {
        console.error('Error fetching data:', error);
    });
}
function BpControlchart(data,orgLevel) {
    var bp_control_data=data.bp_control;
    var key='Female';
    if(Object.keys(bp_control_data).includes('false')){
        key='false'
    }
    var categories = Object.keys(bp_control_data[key]); // Get the facility names from any of the genders
    var maleData = [];
    var femaleData = [];
    var unknownData = [];
    var lowRiskData=[];
    var highRiskData=[];
    var seriesData=[];

    if(key =='Female'){
    categories.forEach(function (facility) {
        maleData.push(bp_control_data['Male'][facility]);
        femaleData.push(bp_control_data['Female'][facility]);
        unknownData.push(bp_control_data['Unknown'][facility]);
    });
    seriesData=[{
        name: 'Male',
        data: maleData
    }, {
        name: 'Female',
        data: femaleData
    }, {
        name: 'Unknown',
        data: unknownData
    }]
    }else{
        categories.forEach(function (facility) {
            lowRiskData.push(bp_control_data['false'][facility]);
            highRiskData.push(bp_control_data['true'][facility]);
        });
        seriesData=[{
            name: 'High Risk',
            data: highRiskData,
            color:'#FF5733',
        }, {
            name: 'Low Risk',
            data: lowRiskData,
            color:'#00008B',
        },]
    }
    // Render Highcharts graph
    Highcharts.chart('bp_control', {
        chart: {
            type: 'column'
        },
        credits: {
            text: "Powered by Smockin", // Custom text
            href: "https://github.com/smockin", // Custom link
            target: "_blank",
            position: {
              align: "right",
              x: -10,
              verticalAlign: "bottom",
              y: -5,
            },
          },
        title: {
            text: `Blood Pressure Control: ${orgLevel} by Facility`
        },
        xAxis: {
            categories: categories,
            crosshair: true
        },
        yAxis: {
            title: {
                text: 'Controlled Blood Pressure (%)'
            },
            labels: {
                format: "{value:.1f}%",
              },
        },
        tooltip: {
            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of total<br/>'
        },
          legend: {
            layout: "horizontal",
            align: "left",
            x: 80,
            verticalAlign: "top",
            y: 5,
            floating: true,
            backgroundColor:
              Highcharts.defaultOptions.legend.backgroundColor || // theme
              "rgba(255,255,255,0.25)",
          },
        series: seriesData,
    });
}
function BpMedsControlchart(data, orgLevel) {
    var meds_data = data.bp_meds;
    console.log(meds_data);
    var categories = Object.keys(meds_data); // Get the facility names
    var seriesData = [{
        name: 'Percentage of core medicine available',
        colorByPoint: true,
        data: []
    }];
    console.log(seriesData);
    // Iterate over the categories (facilities) and push data to seriesData array
    categories.forEach(function(facility) {
        let availablePercentage = meds_data[facility];
        seriesData[0].data.push(
        {
            name: facility,
            y:availablePercentage,
            drilldown: facility
        });
    });
console.log(seriesData)
    // Render Highcharts graph
    Highcharts.chart('bp_control_meds', {
        chart: {
            type: 'column'
        },
        credits: {
            text: "Powered by Smockin", // Custom text
            href: "https://github.com/smockin", // Custom link
            target: "_blank",
            position: {
              align: "right",
              x: -10,
              verticalAlign: "bottom",
              y: -5,
            },
          },
        title: {
            align: 'left',
            text: `Availability of diabetes core medicines: ${orgLevel} by Facility`
        },
        accessibility: {
            announceNewData: {
                enabled: true
            }
        },
        xAxis: {
            type: 'category'
        },
        yAxis: {
            title: {
                text: 'Percentage of core medicine available (%)'
            },
            min:0,
            max:120,
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true,
                    format: '{point.y:.1f}%'
                }
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:11px">Percentage of Core Blood pressure control medicine available</span><br>',
            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of total<br/>'
        },
    
        series: seriesData,
        
    });
}


fetchDataAndRenderGraphs(group_by='gender');   
$('#group_by').change(function () {
    group_by = $(this).val();
    console.log(group_by);
    fetchDataAndRenderGraphs(group_by)
});  
});
