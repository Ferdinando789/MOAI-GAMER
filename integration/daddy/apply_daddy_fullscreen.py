#!/usr/bin/env python3
"""Add bounded DaddyLive retry and startup watchdog to fullscreen playback only."""
from pathlib import Path
import sys

p=Path(sys.argv[1])/"app/src/main/java/com/infomak/moailite/PlayerActivity.java"
s=p.read_text(encoding="utf-8")
needle='    private int generation; private boolean started,recorded;'
assert s.count(needle)==1
s=s.replace(needle,needle+'''
    private int daddyRetries;
    private final android.os.Handler daddyHandler =
        new android.os.Handler(android.os.Looper.getMainLooper());
''',1)
needle='        current=c;recorded=false;title.setText(c.getNombre());updateButtons();'
assert s.count(needle)==1
s=s.replace(needle,'''        daddyHandler.removeCallbacksAndMessages(null);
        daddyRetries=0;
'''+needle,1)
needle='    private void resolve(String id){'
assert s.count(needle)==1
helper='''    /** Timed reconnects are restricted to DaddyLive; other channels are unaffected. */
    private boolean retryDaddy(String reason) {
        if (current==null || current.getId()==null ||
            !current.getId().startsWith("moai_daddylive:") ||
            isFinishing() || isDestroyed() || daddyRetries>=3) return false;
        final String id=current.getId();
        final int request=generation;
        final int attempt=++daddyRetries;
        android.util.Log.w("MOAI-DADDY", "Fullscreen retry "+attempt+"/3: "+reason);
        if(player!=null){playerView.setPlayer(null);player.release();player=null;}
        status.setText("DaddyLive: reintentando "+attempt+"/3…");
        daddyHandler.postDelayed(()->{
            if(!isFinishing()&&!isDestroyed()&&generation==request&&
               current!=null&&id.equals(current.getId())) resolve(id);
        },attempt*2000L);
        return true;
    }
'''
s=s.replace(needle,helper+needle,1)
needle='''    }catch(Exception e){runOnUiThread(()->{if(request==generation&&!isDestroyed())status.setText("Error: "+rootMessage(e));});}});}'''
replacement='''    }catch(Exception e){runOnUiThread(()->{
        if(request==generation&&!isDestroyed()&&!isFinishing() &&
           !retryDaddy(rootMessage(e)))status.setText("Error: "+rootMessage(e));
    });}});}'''
assert s.count(needle)==1
s=s.replace(needle,replacement,1)
needle='''                @Override public void onPlaybackStateChanged(int state){if(state==Player.STATE_READY){status.setText("En vivo");}else if(state==Player.STATE_BUFFERING)status.setText("Cargando…");}'''
replacement='''                @Override public void onPlaybackStateChanged(int state){
                    if(state==Player.STATE_READY){status.setText("En vivo");daddyRetries=0;}
                    else if(state==Player.STATE_BUFFERING)status.setText("Cargando señal…");
                }'''
assert s.count(needle)==1
s=s.replace(needle,replacement,1)
needle='''                @Override public void onPlayerError(PlaybackException error){status.setText("Error de reproducción: "+error.getErrorCodeName());}'''
replacement='''                @Override public void onPlayerError(PlaybackException error){
                    if(!retryDaddy(error.getErrorCodeName()))
                        status.setText("Error de reproducción: "+error.getErrorCodeName());
                }'''
assert s.count(needle)==1
s=s.replace(needle,replacement,1)
needle='''            player.prepare(); player.setPlayWhenReady(started);
        }catch(Exception e){status.setText("Error: "+rootMessage(e));}'''
replacement='''            final int request=generation;
            final int attempt=daddyRetries;
            final String channelId=current==null?"":current.getId();
            if(channelId.startsWith("moai_daddylive:")) {
                daddyHandler.postDelayed(()->{
                    if(request==generation && attempt==daddyRetries &&
                       current!=null && channelId.equals(current.getId()) &&
                       player!=null && player.getPlaybackState()!=Player.STATE_READY)
                        if(!retryDaddy("45 seconds without ready state"))
                            status.setText("DaddyLive no respondió tras varios intentos.");
                },45000L);
            }
            player.prepare(); player.setPlayWhenReady(started);
        }catch(Exception e){
            if(!retryDaddy(rootMessage(e)))status.setText("Error: "+rootMessage(e));
        }'''
assert s.count(needle)==1
s=s.replace(needle,replacement,1)
needle='''    @Override protected void onDestroy(){generation++;if(player!=null){player.release();player=null;} worker.shutdownNow();super.onDestroy();}'''
replacement='''    @Override protected void onDestroy(){
        generation++;daddyHandler.removeCallbacksAndMessages(null);
        if(player!=null){player.release();player=null;}
        worker.shutdownNow();super.onDestroy();
    }'''
assert s.count(needle)==1
s=s.replace(needle,replacement,1)
p.write_text(s,encoding="utf-8")
print("MOAI DaddyLive fullscreen: 45 s watchdog and 3 retries with capped backoff")
