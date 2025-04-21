'use client';
import React, { useRef, useState, useEffect, ReactNode } from 'react';
import { motion, useInView } from 'framer-motion';
import styles from './AnimatedList.module.css';

interface AnimatedItemProps {
  children: ReactNode;
  delay?: number;
  index: number;
  onMouseEnter?: () => void;
  onClick?: () => void;
}
const AnimatedItem: React.FC<AnimatedItemProps> = ({ children, delay = 0, index, onMouseEnter, onClick }) => {
  const ref = useRef<HTMLLIElement>(null);
  const inView = useInView(ref, { amount: 0.5, once: true });

  return (
    <motion.li
      ref={ref as any}
      data-index={index}
      onMouseEnter={onMouseEnter}
      onClick={onClick}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : { scale: 0.9, opacity: 0 }}
      transition={{ duration: 0.3, delay }}
      className={`${styles.itemWrapper} ${inView ? styles.selected : ''}`}
    >
      {children}
    </motion.li>
  );
};

interface AnimatedListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  onItemSelect?: (item: T, index: number) => void;
  displayScrollbar?: boolean;
  className?: string;
  initialSelectedIndex?: number;
}
const AnimatedList = <T extends unknown>({
  items,
  renderItem,
  onItemSelect,
  displayScrollbar = true,
  className = '',
  initialSelectedIndex = -1,
}: AnimatedListProps<T>) => {
  const listRef = useRef<HTMLUListElement>(null);
  const [selectedIndex, setSelectedIndex] = useState(initialSelectedIndex);
  const [topOpacity, setTopOpacity] = useState(0);
  const [bottomOpacity, setBottomOpacity] = useState(1);

  const handleScroll = (e: React.UIEvent<HTMLUListElement>) => {
    const target = e.currentTarget;
    const top = target.scrollTop;
    const max = target.scrollHeight - target.clientHeight;
    setTopOpacity(Math.min(top / 30, 1));
    setBottomOpacity(max <= 0 ? 0 : Math.min((max - top) / 30, 1));
  };

  return (
    <div className={`${styles.scrollListContainer} ${className}`}>      
      <ul
        ref={listRef as any}
        className={`${displayScrollbar ? '' : styles.noScrollbar} ${styles.scrollList}`}
        onScroll={handleScroll}
      >
        {items.map((item, idx) => (
          <AnimatedItem
            key={idx}
            delay={0.05 * idx}
            index={idx}
            onMouseEnter={() => setSelectedIndex(idx)}
            onClick={() => {
              setSelectedIndex(idx);
              onItemSelect?.(item, idx);
            }}
          >
            {renderItem(item, idx)}
          </AnimatedItem>
        ))}
      </ul>

      {topOpacity > 0 && <div className={styles.topGradient} style={{ opacity: topOpacity }} />}
      {bottomOpacity > 0 && <div className={styles.bottomGradient} style={{ opacity: bottomOpacity }} />}
    </div>
  );
};

export default AnimatedList;