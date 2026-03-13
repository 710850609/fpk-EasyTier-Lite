export async function fetchNigger() {
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