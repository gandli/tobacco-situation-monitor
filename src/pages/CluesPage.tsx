import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ClueList } from '../components/clues/ClueList';
import type { Clue } from '../types';
import { generateClues } from '../data/mockData';

export const CluesPage: React.FC = () => {
  const navigate = useNavigate();
  const clues = React.useMemo(() => generateClues(50), []);

  const handleClueClick = (clue: Clue) => {
    navigate(`/clues/${clue.id}`);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 页面头部 */}
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">
          线索列表
        </h1>
        <p className="text-gray-500 mt-1">违法线索查看和管理</p>
      </div>

      {/* 线索列表（含筛选） */}
      <ClueList clues={clues} onClueClick={handleClueClick} />
    </div>
  );
};