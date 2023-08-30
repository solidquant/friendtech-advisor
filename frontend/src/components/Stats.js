import { useEffect, useState } from 'react';

import HighchartsReact from 'highcharts-react-official';
import Highcharts from 'highcharts/highstock'
import HighchartsExporting from 'highcharts/modules/exporting'

if (typeof Highcharts === 'object') {
    HighchartsExporting(Highcharts)
}

const defaultOptions = {
    title: { text: '' },
    chart: { backgroundColor: 'transparent' },
    credits: { enabled: false },
    exporting: { enabled: false },
    xAxis: {
        visible: false,
        labels: {
            enabled: false,
        },
    },
    yAxis: {
        title: {
            text: null
        },
    },
    series: [{type: 'line', color: '#2d3436', data: [[1, 0]]}],
};

const Stats = ({ socket }) => {
    const [users, setUsers] = useState({block: 0, cnt: 0});
    const [options, setOptions] = useState(defaultOptions);

    useEffect(() => {
        socket.on('event', (evt) => {
            setUsers({
                block: evt.block,
                cnt: evt.users_history.slice(-1)[0][1]
            });
            setOptions({
                ...options,
                series: [{
                    name: 'Users over time',
                    type: 'line',
                    color: '#2d3436',
                    lineWidth: 2,
                    data: evt.users_history,
                    marker: { enabled: false },
                }],
            });
        });
    }, []);

    return (
        <div className="Stats">
            <div className="title">{`⛓ Block #${users.block.toLocaleString()} 📊 Total Users: ${users.cnt.toLocaleString()}`}</div>
            <div className="user-chart">
                <HighchartsReact
                    highcharts={Highcharts}
                    options={options}
                />
            </div>
        </div>
    );
}

export default Stats;