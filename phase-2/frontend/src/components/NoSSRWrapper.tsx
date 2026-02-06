'use client';

import { useState, useEffect, ReactNode } from 'react';

interface NoSSRWrapperProps {
  children: ReactNode;
}

const NoSSRWrapper = ({ children }: NoSSRWrapperProps) => {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted) {
    return null;
  }

  return <>{children}</>;
};

export default NoSSRWrapper;