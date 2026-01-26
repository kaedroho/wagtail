import { useState, useEffect, useRef, Children, cloneElement, isValidElement } from 'react';
import { styled } from '@linaria/react';

const TRANSITION_DURATION = 210;

export const PUSH = 'push';
export const POP = 'pop';

const TransitionWrapper = styled.div`
  position: relative;
  overflow: hidden;

  > * {
    position: absolute;
    width: 100%;
    top: 0;
  }

  /* Push transition */
  .w-transition-push-enter {
    transform: translateX(100%);
  }

  .w-transition-push-enter-active {
    transform: translateX(0);
    transition: transform 200ms ease;
  }

  .w-transition-push-leave {
    transform: translateX(0);
  }

  .w-transition-push-leave-active {
    transform: translateX(-100%);
    transition: transform 200ms ease;
  }

  /* Pop transition */
  .w-transition-pop-enter {
    transform: translateX(-100%);
  }

  .w-transition-pop-enter-active {
    transform: translateX(0);
    transition: transform 200ms ease;
  }

  .w-transition-pop-leave {
    transform: translateX(0);
  }

  .w-transition-pop-leave-active {
    transform: translateX(100%);
    transition: transform 200ms ease;
  }
`;

interface TransitionChild {
  key: string | number;
  element: React.ReactElement;
  state: 'entering' | 'entered' | 'leaving';
}

interface TransitionProps {
  name: typeof PUSH | typeof POP;
  className?: string;
  duration?: number;
  children?: React.ReactNode;
}

export default function Transition({
  name,
  className,
  duration = TRANSITION_DURATION,
  children,
}: TransitionProps) {
  const [items, setItems] = useState<TransitionChild[]>([]);
  const timeoutsRef = useRef<Map<string | number, NodeJS.Timeout>>(new Map());

  useEffect(() => {
    const childArray = Children.toArray(children).filter(isValidElement) as React.ReactElement[];
    const currentChild = childArray[0];
    const currentKey = currentChild?.key ?? 'default';

    setItems((prevItems) => {
      const existingItem = prevItems.find((item) => item.key === currentKey);

      if (existingItem) {
        // Child already exists - update element but keep state
        return prevItems.map((item) =>
          item.key === currentKey ? { ...item, element: currentChild } : item,
        );
      }

      // New child entering - mark old children as leaving
      const newItems: TransitionChild[] = prevItems.map((item) => {
        if (item.state !== 'leaving') {
          // Start leave transition
          const timeout = setTimeout(() => {
            setItems((items) => items.filter((i) => i.key !== item.key));
            timeoutsRef.current.delete(item.key);
          }, duration);
          timeoutsRef.current.set(item.key, timeout);
          return { ...item, state: 'leaving' as const };
        }
        return item;
      });

      if (currentChild) {
        newItems.push({
          key: currentKey,
          element: currentChild,
          state: 'entering',
        });
      }

      return newItems;
    });
  }, [children, duration]);

  // Trigger enter-active on next frame for entering items
  useEffect(() => {
    const enteringItems = items.filter((item) => item.state === 'entering');
    if (enteringItems.length > 0) {
      const frameId = requestAnimationFrame(() => {
        setItems((prevItems) =>
          prevItems.map((item) =>
            item.state === 'entering' ? { ...item, state: 'entered' } : item,
          ),
        );
      });
      return () => cancelAnimationFrame(frameId);
    }
  }, [items]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      timeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
    };
  }, []);

  const prefix = `w-transition-${name}`;

  return (
    <TransitionWrapper className={className}>
      {items.map((item) => {
        let itemClassName = '';
        if (item.state === 'entering') {
          itemClassName = `${prefix}-enter`;
        } else if (item.state === 'entered') {
          itemClassName = `${prefix}-enter ${prefix}-enter-active`;
        } else if (item.state === 'leaving') {
          itemClassName = `${prefix}-leave ${prefix}-leave-active`;
        }

        return cloneElement(item.element, {
          key: item.key,
          className: `${item.element.props.className || ''} ${itemClassName}`.trim(),
        });
      })}
    </TransitionWrapper>
  );
}
