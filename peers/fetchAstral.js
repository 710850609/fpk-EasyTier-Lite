export async function fetchAstral() {
    const url = 'https://astral.fan/server-config/server-list/';
    var response = await fetch(url, {
      method: "GET",
      headers: {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "connection": "keep-alive",
        "host": "www.sbgov.cn",
        "pragma": "no-cache",
        "referer": "http://www.sbgov.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Cookie": cookie,
      },
    });
    var text = await response.text();
    console.log("响应内容: ", text);
    // if (!json || !json.data || !json.data.items) {
    //     console.log("无法获取有效数据");
    //     return [];
    // }
    // var items = json.data.items.sort((a, b) => a.health_percentage_24h - b.health_percentage_24h);
    // // console.log("排序后内容: ", JSON.stringify(items));
    // var address = items.map(e => e.address);
    // // console.log("排序后内容: ", JSON.stringify(address));
    // return address;
    
}