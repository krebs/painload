" /vim/bridge.vim

if ! exists('s:bridge_name')
  let s:bridge_name = ""
endif

fun! Bridge_complete(A,L,P)
    let a = strpart(a:A,0,a:P)
    return split(system("bridge list \"".a.".*\""), "\n")
endfun

fun! Bridge_status()
  if s:bridge_name == ""
    return "Disconnected"
  else
    return "Connected to " . s:bridge_name
  else
  endif
endfun

setlocal statusline=%<%f\ \(%{Bridge_status()}\)\ %h%m%r%=%-14.(%l,%c%V%)\ %P\ of\ %L\ \(%.45{getcwd()}\)

fun! Bridge_display()
  if s:bridge_name == ""
    echo "Not connected!"
    return
  endif
  let cmd = "bridge attach ".s:bridge_name
  silent exe "!" . cmd
  redraw!
endfun

fun! Bridge_connect()
  if s:bridge_name == ""
    let m = "boot new"
  else
    let m = s:bridge_name
  endif
  let name = input("Connect to [".m."]: ", "", "customlist,Bridge_complete")
  if name == ""
    if s:bridge_name != ''
      " stay connected
      echo
      return
    endif
    let system = input("Command: ", "")
    if system == ""
        echo "Aborted!"
	return
    endif
    let name = input("Session name: ", "")
    if name == ""
        echo "Aborted!"
	return
    endif
    TODO_boot_new
  endif
  if system("bridge list ".name) == ""
    echo "No such session: ".name
    return
  endif
  let s:bridge_name = name
  let s:laststatus = &laststatus
  let &laststatus = 2
  echo "Connected to " . s:bridge_name
endfun

fun! Bridge_disconnect(m)
  if s:bridge_name == ""
    echo "Not connected!"
  else
    let &laststatus = s:laststatus
    let m = "Disconnected from ".s:bridge_name
    if a:m != ""
      let m .= ": ".a:m
    endif
    echo m."!"
    let s:bridge_name = ""
  endif
endfun

function! Bridge_paste( data )
  if a:data == ''
    echo "Nothing to send!"
  else
    let l:data = a:data
    if exists("g:bridge_prologue") | let l:data = g:bridge_prologue . l:data | endif
    if exists("g:bridge_epilogue") | let l:data = l:data . g:bridge_epilogue | endif
    call system("bridge paste " . s:bridge_name, l:data . "\<cr>")
  endif
endfunction

nmap <C-F12> :call Bridge_display()<cr>
nmap [24^ <C-F12>
nmap <F12> :call Bridge_connect()<cr>
nmap <S-F12> :call Bridge_disconnect("")<cr>
nmap [24$ <S-F12>

nmap <leader>el :call Bridge_paste(getline("."))<cr>
nmap <leader>ec m'ya(:call Bridge_paste(getreg('"'))<cr>`'
nmap <leader>et m'(y%:call Bridge_paste(getreg('"'))<cr>`'

nmap <leader>ee :call Bridge_paste(input("paste: ", ""))<cr>

" sugar
nmap <Return> <leader>ec

"" visual shell
vmap <return> m'y:call Bridge_paste(getreg('"'))<cr>v`'
vmap <leader>ee :call Bridge_paste(input("paste: ", ""))<cr>
vmap <leader>et <return>


