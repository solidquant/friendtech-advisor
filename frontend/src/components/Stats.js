import { useEffect, useState } from 'react';
import { createChart } from 'lightweight-charts';

const Stats = () => {
    const [users, setUsers] = useState(0);

    useEffect(() => {
        const chartOptions = { layout: { textColor: 'black', background: { type: 'solid', color: 'white' } }, autoSize: true };
        const userChart = createChart(document.getElementsByClassName('user-chart')[0], chartOptions);
        const areaSeries = userChart.addAreaSeries({
            lineColor: '#2962FF', topColor: '#2962FF',
            bottomColor: 'rgba(41, 98, 255, 0.28)',
        });
        const data = [
            { time: '2018-12-22', value: 32.51 },
            { time: '2018-12-23', value: 31.11 },
            { time: '2018-12-24', value: 27.02 },
            { time: '2018-12-25', value: 27.32 },
            { time: '2018-12-26', value: 25.17 },
            { time: '2018-12-27', value: 28.89 },
            { time: '2018-12-28', value: 25.46 },
            { time: '2018-12-29', value: 23.92 },
            { time: '2018-12-30', value: 22.68 },
            { time: '2018-12-31', value: 22.67 },
        ];
        areaSeries.setData(data);
        userChart.timeScale().fitContent();

        setUsers(data[data.length - 1].value);
    }, []);

    return (
        <div className="Stats">
            <div className="title">{`📊 Total Users: ${users}`}</div>
            <div className="user-chart"></div>
        </div>
    );
}

export default Stats;