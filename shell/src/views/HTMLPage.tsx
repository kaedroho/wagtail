import {
  NavigationContext,
  useShouldReloadCallback,
} from '@django-bridge/react';
import React, { useCallback, useContext, useEffect, useState } from 'react';
import Layout from '../components/Layout';

interface LoadFrameEvent {
  type: 'load';
  title: string;
}

interface NavigateFrameEvent {
  type: 'navigate';
  url: string;
}

interface SubmitFormFrameEvent {
  type: 'submit-form';
  action: string;
  method: 'get' | 'post';
  data: FormData;
}

interface OpenModalFrameEvent {
  type: 'open-modal';
  url: string;
}

type FrameEvent =
  | LoadFrameEvent
  | NavigateFrameEvent
  | SubmitFormFrameEvent
  | OpenModalFrameEvent;

const frameCallbacks: { [id: number]: (event: FrameEvent) => void } = {};

window.addEventListener('message', (event) => {
  if (event.data.id in frameCallbacks) {
    frameCallbacks[event.data.id](event.data);
  }
});

interface HTMLPageProps {
  frameUrl: string;
  html: string;
}

export default function Frame({ frameUrl, html }: HTMLPageProps) {
  const {
    frameId: currentFrameId,
    path,
    navigate,
    submitForm,
  } = useContext(NavigationContext);
  const [frontFrameId, setFrontFrameId] = useState(currentFrameId);
  const [backFrameId, setBackFrameId] = useState<number | null>(currentFrameId);

  useShouldReloadCallback(() => false, []);

  useEffect(() => {
    setBackFrameId(currentFrameId);
  }, [currentFrameId, frontFrameId]);

  const onIframeLoad = useCallback(
    (frameId: number, e: React.SyntheticEvent<HTMLIFrameElement>) => {
      if (e.target instanceof HTMLIFrameElement && e.target.contentWindow) {
        e.target.contentWindow.postMessage(
          {
            html,
            path,
            frameId,
          },
          '*',
        );

        frameCallbacks[frameId] = (event) => {
          if (event.type === 'load') {
            setFrontFrameId(frameId);
            if (backFrameId && backFrameId <= frameId) {
              setBackFrameId(null);
            }
          }

          if (event.type === 'navigate') {
            navigate(event.url);
          }

          if (event.type === 'submit-form') {
            if (event.method === 'get') {
              // TODO: Make sure there are no files here
              const dataString = Array.from(event.data.entries())
                .map(
                  (x) =>
                    `${encodeURIComponent(x[0])}=${encodeURIComponent(x[1] as string)}`,
                )
                .join('&');

              const url =
                event.action +
                (event.action.indexOf('?') === -1 ? '?' : '&') +
                dataString;
              navigate(url);
            } else {
              submitForm(event.action, event.data);
            }
          }
        };
      }
    },
    [backFrameId, html, path, navigate, submitForm],
  );

  const frames = [];

  if (backFrameId) {
    frames.push(
      <iframe
        title={`Wagtail Frame ${backFrameId}`}
        key={backFrameId}
        style={{
          border: 'none',
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
        onLoad={(e) => onIframeLoad(backFrameId, e)}
        src={frameUrl}
      />,
    );
  }

  if (frontFrameId !== backFrameId) {
    frames.push(
      <iframe
        title={`Wagtail Frame ${frontFrameId}`}
        key={frontFrameId}
        style={{
          border: 'none',
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
        onLoad={(e) => onIframeLoad(frontFrameId, e)}
        src={frameUrl}
      />,
    );
  }

  return <Layout>{frames}</Layout>;
}
