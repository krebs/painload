// ==UserScript==
// @name           Krebs Affiliate Programs + extras (auto-SSL...)
// @namespace      https://blogs.fsfe.org/h2/userscripts/
// @description    Modify Amazon to support Krebs, always use SSL and shorten links (only Amazon)

// Contains the getASIN()-function from:
// http://userscripts.org/scripts/review/3284 by Jim Biancolo

// shamelessly stolen from 
// http://userscripts.org/scripts/show/129547
// 

// @version        0.321
// @include       *
// @license       CC0 / Do what the fuck you want to license
// see http://creativecommons.org/publicdomain/zero/1.0/

// @author Hannes Hauswedell
// @author makefu
// @homepage http://euer.krebsco.de
// ==/UserScript==



function getASIN(href) {
    var asinMatch;
    asinMatch = href.match(/\/exec\/obidos\/ASIN\/(\w{10})/i);
    if (!asinMatch) { asinMatch = href.match(/\/gp\/product\/(\w{10})/i); }
    if (!asinMatch) { asinMatch = href.match(/\/exec\/obidos\/tg\/detail\/\-\/(\w{10})/i); }
    if (!asinMatch) { asinMatch = href.match(/\/dp\/(\w{10})/i); }
    if (!asinMatch) { return null; }
    return asinMatch[1];
}

(function()
{
    var links = document.getElementsByTagName("a");

    for (i = 0; i < links.length; i++) 
    {
        var curLink = links[i].href;

        // AMAZON
        if (curLink.match(/https?\:\/\/(www\.)?amazon\./i))
        {
            var affiliateID = '';
            var host = '';
            if (curLink.match(/amazon\.de/i))
            {
                host = 'amazon.de';
                affiliateID = 'krebsco-21';
            }
            else if (curLink.match(/amazon\.co\.uk/i))
            {
                host = 'amazon.co.uk';
                affiliateID = 'krebscode-21';
            }
            else if (curLink.match(/amazon\.ca/i))
            {
                host = 'amazon.ca';
                affiliateID = 'krebscoca-20';
            }
            else if (curLink.match(/amazon\.fr/i))
            {
                host = 'amazon.fr';
                affiliateID = 'krebscode01-21';
            }
            else if (curLink.match(/amazon\.es/i))
            {
                host = 'amazon.es';
                affiliateID = 'krebscode0f-21';
            }
            else if (curLink.match(/amazon\.it/i))
            {
                host = 'amazon.it';
                affiliateID = 'krebscode04-21';
            }
            else if (curLink.match(/amazon\.com/i))
            {
                host = 'amazon.com';
                affiliateID = 'krebsco-20';
            }

            var asin = getASIN(curLink);
            if (affiliateID != '')
            {
                if (asin != null)
                    links[i].setAttribute("href", "https://www."+host+"/dp/" + asin + "/?tag="+affiliateID);
//                 else
//                     links[i].setAttribute("href", curLink + "?tag="+affiliateID);
            }
        }

    }
})();
