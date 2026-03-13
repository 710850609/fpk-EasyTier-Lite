async function fetchNigger() {
  var url = "http://nigger.com.cn:1000/api/nodes?page=1&per_page=50&is_active=true";
  var response = await fetch(url);
  var json = await response.json();
  // console.log("响应内容: ", JSON.stringify(json));
  if (!json || !json.data || !json.data.items) {
    console.log("无法获取有效数据");
    return [];
  }
  var items = json.data.items.sort((a, b) => a.health_percentage_24h - b.health_percentage_24h);
  // console.log("排序后内容: ", JSON.stringify(items));
  var address = items.map(e => e.address);
  // console.log("排序后内容: ", JSON.stringify(address));
  return address;
}

async function fetchSbgov() {
  var url = "http://www.sbgov.cn/api/v1/endpoints/statuses?page=1&pageSize=50";
  // 第一次请求获取 cookie
  var response = await fetch(url, {
    method: "GET",
    headers: {
      "Accept-Encoding": "application/json",
    },
  });

  var html = await response.text();
  // 提取 cookie
  var cookieMatch = html.match(/document\.cookie = '([^']+)'/);
  if (cookieMatch) {
    var cookie = cookieMatch[1];
    console.log("获取到 cookie:", cookie);
    
    // 第二次请求带上 cookie
    var response2 = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Cookie": cookie,
        "host": "http://www.sbgov.cn/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      },
    });
    var json = await response2.text();
    // console.log(json)
    json = JSON.parse(json);
  } else {
    console.log("无法获取 cookie");
    console.log(html)
    json = JSON.parse(html);
  }
  // console.log(json);
  // 提取 group = "αEasyTier 服务器 点进看详情" 的所有元素的 key
  var address = (json || []).filter(e => {
    return e.group === "αEasyTier服务器 点进看详情";
  })
  .filter(e => {
    // 最少最近有3次检测健康
    if ((e.results || []).length > 3) {
      const checkTimes = e.results.length 
      return e.results[checkTimes-1].success && e.results[checkTimes-2].success && e.results[checkTimes-3].success;
    }
    return false;
  })
  .map(e => {
    const proIndex = e.name.lastIndexOf("://");
    return e.name.substring(proIndex-3, e.name.length);
  });
  console.log("排序后内容: ", JSON.stringify(address));
  return address;
}

async function fetchPeers() {
  const peersList = await Promise.all([
    fetchNigger(), 
    fetchSbgov()
  ]);
  const peers = peersList.flat();
  console.log(peers)
}

fetchPeers();