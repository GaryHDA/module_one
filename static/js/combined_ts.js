Highcharts.chart('combined-ts', {
    chart: {
        type: 'scatter',
        plotBorderWidth:0,
        spacingBottom: 20,
        zoomType: 'x',
        style: {
          fontFamily: 'sans-serif',
        }
    },
    title: {
        text: null,
        style:{
          fontSize: '16px',
          color:'#0A2E5C',

        },
    },
    credits:{
      text:'hammerdirt 2018',

    },
    exporting: {
      enabled:false,
    },
    legend: {
      enabled: true,
      verticalAlign: 'top',
      horizontalAlign: 'left',
      layout:'vertical',
      floating:true,
      x:-30,
      y:20,
      backgroundColor:'rgba(255,255,255, .4)',
      borderColor:'rgba(10, 46, 92, .5)',
      borderWidth:1,
      itemMarginTop:4,
      itemMarginBottom:4,
      itemStyle:{
        color: 'black',
        fontSize: 14,
        fontWeight: 'bold',
      }
    },
    xAxis: {
      type: 'datetime',
      tickInterval:3600*1000*24*28*2,
      labels: {
        style: {
          color:'rgba(00, 00, 00, 1)'
        }
      },
      dateTimeLabelFormats: {
        month: '%b - %Y',
      },
    },
    yAxis: {
        title: {
            align: 'low',
            offset: 40,
            text: 'Pieces of trash per meter of shoreline',
            style:{
              fontSize: '12px',
              color:'#000000',
            },
        },
        gridLineColor:'rgba(10, 46, 92, .1)',
        labels:{
          style: {
            color:'rgba(00, 00, 00, 1)'
          }
        },
        tickInterval: 8,
        min: 0,

    },
    tooltip: {
        headerFormat: '<b>{point.key}</b><br>',
        pointFormat: '{point.x:%e-%b}: {point.y:.2f} pcs/m'
    },
    plotOptions:{
      series: {
        turboThreshold: 2000
      }
    },
    series: [
      {
      zIndex:3,
      type: 'scatter',
      name:'Results per inventory',
      marker: {
        symbol: 'circle',
        radius:6,
        lineColor: 'rgba(255, 00, 00, .8)',
        fillColor:  'rgba(255, 65, 168, .6)',
        lineWidth:1,
      },
      data:all_item_data_scatter,

    }
  ],
  }
);
