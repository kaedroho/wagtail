import { NavigationContext } from '@django-bridge/react';
import { useContext } from 'react';

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
  html: string;
  frameUrl: string;
}

export default function Frame({ html, frameUrl }: HTMLPageProps) {
  const { path, frameId, navigate, submitForm } = useContext(NavigationContext);
  const onIframeLoad = (e: React.SyntheticEvent<HTMLIFrameElement>) => {
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
        if (event.type == 'load') {
          /*if (onLoad) {
            onLoad(event.title);
            }*/
        }

        if (event.type == 'navigate') {
          navigate(event.url);
        }

        if (event.type == 'submit-form') {
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
              (event.action.indexOf('?') == -1 ? '?' : '&') +
              dataString;
            navigate(url);
          } else {
            submitForm(event.action, event.data);
          }
        }

        if (event.type == 'open-modal') {
          /*
          if (openModal) {
            openModal(event.url);
            }*/
        }
      };
    }
  };

  return (
    <>
      <iframe
        style={{
          border: 'none',
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
        onLoad={onIframeLoad}
        src={frameUrl}
      />
    </>
  );
}
