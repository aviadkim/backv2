import React from 'react';
import FinDocUI from '../components/FinDocUI';
import RagMultimodalProcessor from '../components/RagMultimodalProcessor';

const RagProcessorPage = () => {
  return (
    <FinDocUI title="RAG Multimodal Financial Document Processor">
      <RagMultimodalProcessor />
    </FinDocUI>
  );
};

export default RagProcessorPage;
