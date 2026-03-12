import React from 'react';
import { CaseDetail } from '../components/cases/CaseDetail';
import { generateClues, generateCase } from '../data/mockData';

export const CasesPage: React.FC = () => {
  // 生成示例案件用于演示
  const caseData = React.useMemo(() => {
    const clues = generateClues(1);
    return generateCase(clues[0]);
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面头部 */}
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">
          案件详情
        </h1>
        <p className="text-gray-500 mt-1">查看案件详细信息、证据和时间线</p>
      </div>

      {/* 案件详情 */}
      <CaseDetail caseData={caseData} />
    </div>
  );
};