import { Clue, Case, GraphData, DashboardStats, TrendData, PlatformStats } from '../types';

const platforms = ['淘宝', '京东', '拼多多', '抖音', '快手', '微信', '闲鱼', '转转'];
const provinces = ['广东省', '浙江省', '江苏省', '山东省', '河南省', '四川省', '湖北省', '福建省'];
const cities: Record<string, string[]> = {
  '广东省': ['广州市', '深圳市', '东莞市', '佛山市', '中山市'],
  '浙江省': ['杭州市', '宁波市', '温州市', '绍兴市', '嘉兴市'],
  '江苏省': ['南京市', '苏州市', '无锡市', '常州市', '南通市'],
  '山东省': ['济南市', '青岛市', '烟台市', '潍坊市', '临沂市'],
  '河南省': ['郑州市', '洛阳市', '开封市', '新乡市', '南阳市'],
  '四川省': ['成都市', '绵阳市', '德阳市', '宜宾市', '泸州市'],
  '湖北省': ['武汉市', '宜昌市', '襄阳市', '荆州市', '黄石市'],
  '福建省': ['福州市', '厦门市', '泉州市', '漳州市', '莆田市'],
};

const districts = ['朝阳区', '海淀区', '浦东新区', '南山区', '天河区', '福田区', '江干区', '拱墅区'];
const productTypes = ['中华香烟', '黄鹤楼香烟', '利群香烟', '玉溪香烟', '芙蓉王香烟', '南京香烟', '云烟', '红塔山香烟'];
const tags = ['假烟', '走私烟', '无证经营', '网络销售', '跨区域', '团伙作案', '重复违法', '高风险'];

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomDate(start: Date, end: Date): string {
  const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return date.toISOString();
}

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

function calculateRiskLevel(score: number): 'low' | 'medium' | 'high' | 'critical' {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

function generateClue(index: number): Clue {
  const province = randomItem(provinces);
  const city = randomItem(cities[province]);
  const riskScore = randomInt(20, 95);
  const createTime = randomDate(new Date('2024-01-01'), new Date('2024-03-12'));
  
  return {
    id: `clue-${generateId()}`,
    merchantName: `${randomItem(['张', '李', '王', '刘', '陈', '杨', '赵', '黄'])}${randomItem(['某', '先生', '女士'])}烟草店`,
    platform: randomItem(platforms),
    productDescription: `${randomItem(productTypes)} ${randomInt(1, 10)}条装`,
    price: randomInt(50, 500),
    originalPrice: randomInt(100, 800),
    location: {
      province,
      city,
      district: randomItem(districts),
      address: `${city}${randomItem(districts)}${randomItem(['人民路', '建设路', '中山路', '解放路', '和平路'])}${randomInt(1, 200)}号`,
      lat: 23.0 + Math.random() * 10,
      lng: 113.0 + Math.random() * 15,
    },
    riskScore,
    riskLevel: calculateRiskLevel(riskScore),
    status: randomItem(['pending', 'investigating', 'resolved', 'dismissed']),
    createTime,
    updateTime: randomDate(new Date(createTime), new Date('2024-03-12')),
    evidence: [],
    relatedEntities: [],
    tags: [randomItem(tags), randomItem(tags)].filter((v, i, a) => a.indexOf(v) === i),
  };
}

export function generateClues(count: number = 50): Clue[] {
  return Array.from({ length: count }, (_, i) => generateClue(i));
}

export function generateGraphData(): GraphData {
  const nodes = [
    { id: 'm1', type: 'merchant' as const, name: '张三烟草店', riskScore: 85, properties: { location: '广州市天河区' } },
    { id: 'm2', type: 'merchant' as const, name: '李四烟酒行', riskScore: 72, properties: { location: '深圳市南山区' } },
    { id: 'm3', type: 'merchant' as const, name: '王五便利店', riskScore: 45, properties: { location: '东莞市莞城区' } },
    { id: 'm4', type: 'merchant' as const, name: '赵六超市', riskScore: 68, properties: { location: '佛山市禅城区' } },
    { id: 'm5', type: 'merchant' as const, name: '陈七烟酒店', riskScore: 91, properties: { location: '中山市石岐区' } },
    { id: 'l1', type: 'logistics' as const, name: '顺丰快递', properties: { code: 'SF' } },
    { id: 'l2', type: 'logistics' as const, name: '圆通快递', properties: { code: 'YTO' } },
    { id: 'l3', type: 'logistics' as const, name: '中通快递', properties: { code: 'ZTO' } },
    { id: 'p1', type: 'person' as const, name: '张三', properties: { role: '店主' } },
    { id: 'p2', type: 'person' as const, name: '李四', properties: { role: '店主' } },
    { id: 'p3', type: 'person' as const, name: '王五', properties: { role: '店主' } },
    { id: 'p4', type: 'person' as const, name: '赵六', properties: { role: '店主' } },
    { id: 'p5', type: 'person' as const, name: '陈七', properties: { role: '店主' } },
    { id: 'p6', type: 'person' as const, name: '周八', properties: { role: '供应商' } },
    { id: 'p7', type: 'person' as const, name: '吴九', properties: { role: '供应商' } },
  ];

  const edges = [
    { id: 'e1', source: 'p1', target: 'm1', type: 'owns' as const, weight: 1, properties: {} },
    { id: 'e2', source: 'p2', target: 'm2', type: 'owns' as const, weight: 1, properties: {} },
    { id: 'e3', source: 'p3', target: 'm3', type: 'owns' as const, weight: 1, properties: {} },
    { id: 'e4', source: 'p4', target: 'm4', type: 'owns' as const, weight: 1, properties: {} },
    { id: 'e5', source: 'p5', target: 'm5', type: 'owns' as const, weight: 1, properties: {} },
    { id: 'e6', source: 'p6', target: 'm1', type: 'supplies' as const, weight: 0.8, properties: { frequency: 'high' } },
    { id: 'e7', source: 'p6', target: 'm2', type: 'supplies' as const, weight: 0.7, properties: { frequency: 'medium' } },
    { id: 'e8', source: 'p7', target: 'm3', type: 'supplies' as const, weight: 0.6, properties: { frequency: 'low' } },
    { id: 'e9', source: 'p7', target: 'm5', type: 'supplies' as const, weight: 0.9, properties: { frequency: 'high' } },
    { id: 'e10', source: 'm1', target: 'l1', type: 'delivers' as const, weight: 0.8, properties: { volume: 'large' } },
    { id: 'e11', source: 'm2', target: 'l2', type: 'delivers' as const, weight: 0.7, properties: { volume: 'medium' } },
    { id: 'e12', source: 'm3', target: 'l3', type: 'delivers' as const, weight: 0.5, properties: { volume: 'small' } },
    { id: 'e13', source: 'm4', target: 'l1', type: 'delivers' as const, weight: 0.6, properties: { volume: 'medium' } },
    { id: 'e14', source: 'm5', target: 'l2', type: 'delivers' as const, weight: 0.9, properties: { volume: 'large' } },
    { id: 'e15', source: 'p6', target: 'p7', type: 'related' as const, weight: 0.5, properties: { relation: 'partner' } },
    { id: 'e16', source: 'm1', target: 'm2', type: 'related' as const, weight: 0.4, properties: { relation: 'same_supplier' } },
  ];

  return { nodes, edges };
}

export function generateTrendData(): TrendData[] {
  const data: TrendData[] = [];
  const startDate = new Date('2024-02-01');
  
  for (let i = 0; i < 30; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    const totalClues = 100 + randomInt(-20, 50) + i * 2;
    const newClues = randomInt(5, 20);
    const resolvedClues = randomInt(3, 15);
    
    data.push({
      date: date.toISOString().split('T')[0],
      totalClues,
      newClues,
      resolvedClues,
      highRiskClues: randomInt(2, 10),
    });
  }
  
  return data;
}

export function generatePlatformStats(): PlatformStats[] {
  const stats = platforms.map(platform => ({
    platform,
    count: randomInt(10, 100),
    percentage: 0,
    avgRiskScore: randomInt(40, 80),
  }));
  
  const total = stats.reduce((sum, s) => sum + s.count, 0);
  stats.forEach(s => {
    s.percentage = Math.round((s.count / total) * 100);
  });
  
  return stats.sort((a, b) => b.count - a.count);
}

export function generateDashboardStats(): DashboardStats {
  const clues = generateClues(50);
  
  return {
    totalClues: clues.length,
    pendingClues: clues.filter(c => c.status === 'pending').length,
    investigatingClues: clues.filter(c => c.status === 'investigating').length,
    resolvedClues: clues.filter(c => c.status === 'resolved').length,
    highRiskCount: clues.filter(c => c.riskLevel === 'high' || c.riskLevel === 'critical').length,
    todayNewClues: randomInt(5, 15),
    weeklyTrend: generateTrendData(),
    platformDistribution: generatePlatformStats(),
    recentClues: clues.slice(0, 10),
  };
}

export function generateCase(clue: Clue): Case {
  return {
    id: `case-${generateId()}`,
    clueId: clue.id,
    caseNumber: `TC${new Date().getFullYear()}${String(randomInt(1, 9999)).padStart(4, '0')}`,
    title: `${clue.merchantName}违法销售烟草案`,
    status: randomItem(['draft', 'submitted', 'approved', 'closed']),
    createTime: clue.createTime,
    updateTime: clue.updateTime,
    summary: `经查，${clue.merchantName}在${clue.platform}平台销售${clue.productDescription}，价格${clue.price}元，涉嫌违法销售烟草制品。`,
    details: `案件详情：\n\n一、基本情况\n当事人${clue.merchantName}，位于${clue.location.province}${clue.location.city}${clue.location.district}${clue.location.address}。\n\n二、违法事实\n${randomItem(['销售假冒伪劣烟草制品', '无证经营烟草制品', '跨区域非法运输烟草', '网络非法销售烟草'])}。\n\n三、证据材料\n1. 现场检查笔录\n2. 当事人陈述\n3. 商品照片\n4. 交易记录\n\n四、处理意见\n建议依法予以行政处罚。`,
    evidence: [
      {
        id: `ev-${generateId()}`,
        type: 'image',
        title: '商品照片',
        description: '涉案商品现场照片',
        createTime: clue.createTime,
      },
      {
        id: `ev-${generateId()}`,
        type: 'screenshot',
        title: '平台截图',
        description: '违法销售页面截图',
        createTime: clue.createTime,
      },
      {
        id: `ev-${generateId()}`,
        type: 'document',
        title: '交易记录',
        description: '平台交易记录导出',
        createTime: clue.createTime,
      },
    ],
    involvedParties: [
      {
        id: `party-${generateId()}`,
        type: 'merchant',
        name: clue.merchantName,
        role: '当事人',
        address: `${clue.location.province}${clue.location.city}${clue.location.district}${clue.location.address}`,
      },
    ],
    timeline: [
      {
        id: `tl-${generateId()}`,
        time: clue.createTime,
        title: '线索发现',
        description: '系统自动发现违法线索',
        type: 'investigation',
      },
      {
        id: `tl-${generateId()}`,
        time: clue.updateTime,
        title: '初步核实',
        description: '执法人员初步核实线索真实性',
        type: 'investigation',
      },
    ],
  };
}